"""
Centralized WhatsApp messaging service using Selenium (WhatsApp Web automation).

Selenium controls Chrome browser to navigate to web.whatsapp.com and send messages.
A message is only marked successful after the Send button is clicked and the message
appears in the chat (verified via DOM inspection).

Requirements for live sending:
- WhatsApp Web must be logged in (will prompt QR code if not)
- Chrome browser with Selenium Manager (no manual driver install needed)
- selenium must be installed
"""

from __future__ import annotations

import logging
import os
import re
import threading
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger('whatsapp')
logger.setLevel(logging.DEBUG)

ADMIN_WHATSAPP_NUMBER = getattr(settings, 'MY_WHATSAPP_NUMBER', '+919822574252')
WHATSAPP_LOG_DIR = os.path.join(settings.BASE_DIR, 'logs')
WHATSAPP_SEND_LOG = os.path.join(WHATSAPP_LOG_DIR, 'whatsapp_send.log')
WHATSAPP_SEND_LOCK = threading.Lock()

# Selenium WebDriver singleton
_driver_instance = None
_driver_lock = threading.Lock()

# Process lock file to prevent multiple instances using same Chrome profile
_PROFILE_LOCK_FILE = os.path.join(settings.BASE_DIR, 'chrome_profile.lock')
_profile_lock_handle = None

# Screenshot directory for debugging
_SCREENSHOT_DIR = os.path.join(settings.BASE_DIR, 'logs', 'screenshots')

# Retry configuration
_MAX_RETRIES = 1
_RETRY_DELAY = 2  # seconds


def _acquire_profile_lock():
    """Acquire a file lock to prevent multiple Chrome instances using the same profile."""
    global _profile_lock_handle
    try:
        # Try to create/open lock file exclusively
        try:
            _profile_lock_handle = open(_PROFILE_LOCK_FILE, 'x')  # Exclusive creation
            logger.info('Acquired Chrome profile lock')
            return True
        except FileExistsError:
            # Lock file exists, check if it's stale (older than 5 minutes)
            try:
                file_age = time.time() - os.path.getmtime(_PROFILE_LOCK_FILE)
                if file_age > 300:  # 5 minutes stale threshold
                    logger.warning('Stale lock file found, removing it')
                    os.remove(_PROFILE_LOCK_FILE)
                    _profile_lock_handle = open(_PROFILE_LOCK_FILE, 'x')
                    logger.info('Acquired Chrome profile lock after removing stale file')
                    return True
                else:
                    logger.warning('Chrome profile already in use by another process')
                    return False
            except Exception as e:
                logger.warning('Could not check lock file age: %s', e)
                return False
    except Exception as e:
        logger.error('Failed to acquire profile lock: %s', e)
        return False


def _release_profile_lock():
    """Release the Chrome profile lock."""
    global _profile_lock_handle
    if _profile_lock_handle:
        try:
            _profile_lock_handle.close()
            if os.path.exists(_PROFILE_LOCK_FILE):
                os.remove(_PROFILE_LOCK_FILE)
            logger.info('Released Chrome profile lock')
        except Exception as e:
            logger.error('Error releasing profile lock: %s', e)
        finally:
            _profile_lock_handle = None


@dataclass
class WhatsAppSendResult:
    success: bool
    phone_number: str
    message_preview: str = ''
    error: Optional[str] = None
    verified_in_log: bool = False
    session_number: str = ADMIN_WHATSAPP_NUMBER
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WhatsAppContactAttempt:
    parent_type: str
    raw_number: str
    phone_number: str
    success: bool = False
    error: Optional[str] = None


@dataclass
class WhatsAppStudentSendResult:
    success: bool
    attempted_numbers: list[str]
    successful_numbers: list[str] = field(default_factory=list)
    failed_numbers: list[str] = field(default_factory=list)
    status: str = 'failed'
    failure_reason: Optional[str] = None
    attempts: list[WhatsAppContactAttempt] = field(default_factory=list)


CONTACT_FIELDS = (
    ('Father', 'father_mobile'),
    ('Mother', 'mother_mobile'),
)


def clean_whatsapp_message(text: str) -> str:
    """
    Centralized helper to clean WhatsApp message text.

    - Convert CRLF to LF
    - Remove extra blank lines (more than one consecutive newline)
    - Strip leading/trailing whitespace
    - Remove unsupported formatting characters (e.g., Unicode surrogates, control chars)
    - Never render Python lists or dictionaries directly
    """
    if not isinstance(text, str):
        # Convert non-string to safe string representation
        if isinstance(text, (list, tuple)):
            return ', '.join(str(item) for item in text)
        if isinstance(text, dict):
            return ', '.join(f'{k}: {v}' for k, v in text.items())
        return str(text)

    # Remove Unicode surrogates and other problematic characters
    # This pattern removes lone surrogates (invalid in WhatsApp)
    text = re.sub(r'[\ud800-\udfff]', '', text)

    # Remove control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Convert CRLF to LF
    text = text.replace('\r\n', '\n')

    # Remove extra blank lines (more than one consecutive newline)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def _ensure_log_dir() -> None:
    os.makedirs(WHATSAPP_LOG_DIR, exist_ok=True)
    os.makedirs(_SCREENSHOT_DIR, exist_ok=True)


def _append_send_log(line: str) -> None:
    _ensure_log_dir()
    with open(WHATSAPP_SEND_LOG, 'a', encoding='utf-8') as log_file:
        log_file.write(line + '\n')


def format_phone_number(mobile: str | None) -> Optional[str]:
    """Normalize an Indian mobile number to +91XXXXXXXXXX."""
    if mobile is None:
        return None

    mobile = str(mobile).strip()
    if not mobile:
        return None

    digits = ''.join(c for c in mobile if c.isdigit())

    if mobile.startswith('+91') and len(mobile) == 13:
        return mobile

    if mobile.startswith('+') and not mobile.startswith('+91'):
        return mobile if '+' in mobile else None

    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith('0') and len(digits) == 11:
        digits = digits[1:]

    if len(digits) == 10:
        return f'+91{digits}'

    return None


def get_ordered_contact_numbers(student) -> list[tuple[str, str]]:
    """Return valid, de-duplicated parent contact numbers in send order."""
    try:
        parent_info = student.parentinfo
    except Exception:
        return []

    contacts: list[tuple[str, str]] = []
    seen: set[str] = set()

    for parent_type, field_name in CONTACT_FIELDS:
        raw_number = getattr(parent_info, field_name, None)
        formatted = format_phone_number(raw_number)
        if raw_number and not formatted:
            logger.warning(
                'WhatsApp contact skipped | student_id=%s | phone=%r | reason=invalid_number',
                getattr(student, 'registration_no', 'unknown'),
                raw_number,
            )
            continue
        if not formatted or formatted in seen:
            continue
        seen.add(formatted)
        contacts.append((parent_type, formatted))

    return contacts


def send_whatsapp_to_student_contacts(
    student,
    message: str,
    *,
    message_type: str,
    send_func=None,
) -> WhatsAppStudentSendResult:
    """
    Send to every valid parent contact independently.

    Send failures are isolated per contact so one bad WhatsApp number, browser
    timeout, or automation error cannot stop the other parent delivery.
    """
    # Clean the message before sending
    clean_msg = clean_whatsapp_message(message)
    send = send_func or send_whatsapp_message
    contacts = get_ordered_contact_numbers(student)
    attempts: list[WhatsAppContactAttempt] = []
    student_id = getattr(student, 'registration_no', 'unknown')

    logger.debug(
        'WhatsApp debug | student_id=%s | type=%s | parent_numbers_attempted=%s',
        student_id,
        message_type,
        [phone_number for _, phone_number in contacts],
    )

    if not contacts:
        failure_reason = 'No valid WhatsApp contact numbers found'
        logger.warning(
            'WhatsApp student send failed | student_id=%s | type=%s | error=%s',
            student_id,
            message_type,
            failure_reason,
        )
        return WhatsAppStudentSendResult(
            success=False,
            attempted_numbers=[],
            successful_numbers=[],
            failed_numbers=[],
            status='failed',
            failure_reason=failure_reason,
            attempts=attempts,
        )

    for parent_type, phone_number in contacts:
        try:
            logger.info('[DEBUG] Sending to parent | student_id=%s | parent=%s | phone=%s', student_id, parent_type, phone_number)
            result = send(phone_number, clean_msg)
            logger.info('[DEBUG] send_whatsapp_message returned | success=%s | phone=%s | error=%s', result.success, result.phone_number, result.error)
        except Exception as exc:
            logger.error('[DEBUG] Contact send exception | student_id=%s | phone=%s | error=%s', student_id, phone_number, str(exc))
            logger.error('[DEBUG] Traceback: %s', traceback.format_exc())
            attempts.append(WhatsAppContactAttempt(
                parent_type=parent_type,
                raw_number=phone_number,
                phone_number=phone_number,
                success=False,
                error=str(exc),
            ))
            continue

        attempts.append(WhatsAppContactAttempt(
            parent_type=parent_type,
            raw_number=phone_number,
            phone_number=result.phone_number,
            success=result.success,
            error=result.error,
        ))

        if not result.success:
            logger.warning('[DEBUG] Contact failed | student_id=%s | phone=%s | error=%s', student_id, result.phone_number, result.error)

    successful_numbers = [
        attempt.phone_number
        for attempt in attempts
        if attempt.success
    ]
    failed_numbers = [
        attempt.phone_number
        for attempt in attempts
        if not attempt.success
    ]

    failure_reason = '; '.join(
        f'{attempt.phone_number}: {attempt.error or "Send failed"}'
        for attempt in attempts
        if not attempt.success
    ) or 'All contact numbers failed'
    result_success = bool(successful_numbers)
    status = 'sent' if successful_numbers else 'failed'
    logger.info('[DEBUG] send_whatsapp_to_student_contacts FINAL RESULT | student_id=%s | type=%s | successful_numbers=%s | failed_numbers=%s | result_success=%s | ui_status=%s | failure_reason=%s',
        student_id,
        message_type,
        successful_numbers,
        failed_numbers,
        result_success,
        status,
        failure_reason,
    )
    result = WhatsAppStudentSendResult(
        success=result_success,
        attempted_numbers=[attempt.phone_number for attempt in attempts],
        successful_numbers=successful_numbers,
        failed_numbers=failed_numbers,
        status=status,
        failure_reason=failure_reason if failed_numbers else None,
        attempts=attempts,
    )
    logger.info('[DEBUG] Returning from send_whatsapp_to_student_contacts | success=%s | status=%s', result.success, result.status)
    return result




def get_driver():
    """
    Get or create the singleton Selenium WebDriver instance.
    Reuses the same Chrome session for the entire batch.
    """
    global _driver_instance
    
    with _driver_lock:
        if _driver_instance is None:
            # Acquire profile lock before creating driver
            if not _acquire_profile_lock():
                raise Exception('Chrome profile is already in use by another process. Please wait for the current batch to complete.')
            
            try:
                logger.info('[DEBUG] Initializing Chrome WebDriver')
                logger.info('[DEBUG] Chrome profile path: %s', os.path.join(settings.BASE_DIR, 'chrome_profile'))
                
                chrome_options = Options()
                chrome_options.add_argument('--user-data-dir=' + os.path.join(settings.BASE_DIR, 'chrome_profile'))
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-first-run')
                chrome_options.add_argument('--disable-default-apps')
                chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Add logging for ChromeDriver
                chrome_options.add_argument('--enable-logging')
                chrome_options.add_argument('--log-level=0')
                
                logger.info('[DEBUG] Chrome options configured')
                
                # Use webdriver-manager to auto-download matching ChromeDriver
                logger.info('[DEBUG] Using webdriver-manager to get ChromeDriver')
                service = Service(ChromeDriverManager().install())
                logger.info('[DEBUG] ChromeDriver service created')
                
                _driver_instance = webdriver.Chrome(service=service, options=chrome_options)
                logger.info('[DEBUG] Chrome WebDriver created successfully')
                
                _driver_instance.set_page_load_timeout(30)
                _driver_instance.maximize_window()
                logger.info('[DEBUG] WebDriver configured (timeout=30, maximized)')
                logger.info('Selenium WebDriver initialized successfully')
            except Exception as e:
                logger.error('Failed to initialize Selenium WebDriver: %s', e)
                logger.error('[DEBUG] Chrome initialization traceback: %s', traceback.format_exc())
                _release_profile_lock()
                raise
        
        # Verify driver is still alive
        try:
            _driver_instance.current_url
        except Exception as e:
            logger.warning('Driver appears to have crashed, reinitializing: %s', e)
            _driver_instance = None
            _release_profile_lock()
            return get_driver()
        
        return _driver_instance


def close_driver():
    """Close the Selenium WebDriver instance and clean up all resources."""
    global _driver_instance
    
    with _driver_lock:
        if _driver_instance is not None:
            try:
                # Close all tabs except the first one
                try:
                    handles = _driver_instance.window_handles
                    for handle in handles[1:]:  # Keep first tab, close others
                        _driver_instance.switch_to.window(handle)
                        _driver_instance.close()
                    if handles:
                        _driver_instance.switch_to.window(handles[0])
                except Exception as e:
                    logger.warning('Error closing tabs: %s', e)
                
                _driver_instance.quit()
                _driver_instance = None
                logger.info('Selenium WebDriver closed successfully')
            except Exception as e:
                logger.error('Error closing WebDriver: %s', e)
            finally:
                # Always release profile lock when closing driver
                _release_profile_lock()
                # Force garbage collection to prevent memory leaks
                import gc
                gc.collect()


def is_selenium_available() -> tuple[bool, Optional[str]]:
    try:
        from selenium import webdriver  # noqa: F401
        return True, None
    except ImportError:
        return False, 'selenium is not installed. Run: pip install selenium'


def send_whatsapp_message(phone_number: str, message: str, wait_time: int = 15) -> WhatsAppSendResult:
    """
    Send a WhatsApp message via Selenium with retry logic and crash recovery.

    Returns WhatsAppSendResult with success=True only when the message is confirmed
    sent via DOM inspection (Send button clicked and message appears in chat).
    """
    # Clean the message before sending
    clean_msg = clean_whatsapp_message(message)
    formatted_phone = format_phone_number(phone_number)
    preview = (clean_msg or '')[:80]

    if not formatted_phone:
        error = f'Invalid phone number: {phone_number!r}'
        logger.error('WhatsApp send failed - %s', error)
        _append_send_log(f'{datetime.now().isoformat()} | FAILED | invalid_number | raw={phone_number!r}')
        return WhatsAppSendResult(
            success=False,
            phone_number=str(phone_number),
            message_preview=preview,
            error=error,
        )

    available, import_error = is_selenium_available()
    if not available:
        logger.error('WhatsApp send failed - %s', import_error)
        _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {import_error}')
        return WhatsAppSendResult(
            success=False,
            phone_number=formatted_phone,
            message_preview=preview,
            error=import_error,
        )

    logger.info(
        'Sending WhatsApp | session=%s | to=%s | preview=%r',
        ADMIN_WHATSAPP_NUMBER,
        formatted_phone,
        preview,
    )
    _append_send_log(
        f'{datetime.now().isoformat()} | ATTEMPT | session={ADMIN_WHATSAPP_NUMBER} | to={formatted_phone} | {preview!r}'
    )

    # Retry loop for internet disconnects
    for attempt in range(_MAX_RETRIES + 1):
        with WHATSAPP_SEND_LOCK:
            try:
                logger.info('[DEBUG] Attempt %d/%d: Getting driver', attempt + 1, _MAX_RETRIES + 1)
                driver = get_driver()
                logger.info('[DEBUG] Driver initialized successfully')
                logger.info('[DEBUG] Chrome profile path: %s', os.path.join(settings.BASE_DIR, 'chrome_profile'))
                
                # Navigate to WhatsApp Web if not already there
                current_url = driver.current_url
                logger.info('[DEBUG] Current URL before navigation: %s', current_url)
                if driver.current_url != 'https://web.whatsapp.com/':
                    logger.info('[DEBUG] Navigating to WhatsApp Web')
                    driver.get('https://web.whatsapp.com/')
                    logger.info('[DEBUG] Navigated to WhatsApp Web')
                
                # Wait for WhatsApp Web to load (check for main interface elements)
                try:
                    logger.info('[DEBUG] Waiting for WhatsApp Web to load (main interface or QR code)')
                    logger.info('[DEBUG] Selectors: [data-testid="chat-list"], [data-testid="side"], canvas[aria-label="Scan this QR code"]')
                    WebDriverWait(driver, 30).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list"]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="side"]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas[aria-label="Scan this QR code"]'))
                        )
                    )
                    logger.info('[DEBUG] WhatsApp Web loaded successfully')
                except Exception as e:
                    logger.error('[DEBUG] WhatsApp Web load timeout: %s', e)
                    logger.error('[DEBUG] Traceback: %s', traceback.format_exc())
                    _take_screenshot(driver, f'load_timeout_{formatted_phone}')
                    
                    # Save DOM source for debugging
                    try:
                        dom_file = os.path.join(_SCREENSHOT_DIR, f'timeout_dom_{formatted_phone}.html')
                        with open(dom_file, 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        logger.info('[DEBUG] Saved DOM source to %s', dom_file)
                    except Exception as dom_error:
                        logger.error('[DEBUG] Failed to save DOM source: %s', dom_error)
                    
                    if attempt < _MAX_RETRIES:
                        logger.info('Retrying after timeout (attempt %d/%d)', attempt + 1, _MAX_RETRIES)
                        time.sleep(_RETRY_DELAY)
                        continue
                    else:
                        error = f'WhatsApp Web load timeout after {attempt + 1} attempts: {e}'
                        logger.error('WhatsApp send failed - %s', error)
                        _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                        return WhatsAppSendResult(
                            success=False,
                            phone_number=formatted_phone,
                            message_preview=preview,
                            error=error,
                        )
                
                # Check if QR code is present (not logged in) - only if main interface not visible
                try:
                    logger.info('[DEBUG] Checking login status (QR code vs main interface)')
                    # First check if main interface is visible (already logged in)
                    try:
                        driver.find_element(By.CSS_SELECTOR, '[data-testid="chat-list"]')
                        logger.info('[DEBUG] Main interface visible - already logged in, proceeding')
                    except:
                        # Main interface not visible, check for QR code
                        qr_code = driver.find_element(By.CSS_SELECTOR, 'canvas[aria-label="Scan this QR code"]')
                        if qr_code:
                            error = 'WhatsApp Web not logged in. Please scan QR code and retry.'
                            logger.error('[DEBUG] QR code detected - not logged in')
                            logger.error('WhatsApp send failed - %s', error)
                            _take_screenshot(driver, f'qr_code_detected_{formatted_phone}')
                            _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                            return WhatsAppSendResult(
                                success=False,
                                phone_number=formatted_phone,
                                message_preview=preview,
                                error=error,
                            )
                        else:
                            logger.info('[DEBUG] Neither QR code nor main interface found - assuming logged in')
                except Exception as e:
                    # Neither QR code nor main interface found, assume logged in and proceed
                    logger.info('[DEBUG] Login check exception: %s - assuming logged in and proceeding', e)
                
                # Open chat with the phone number using JavaScript navigation
                whatsapp_url = f'https://web.whatsapp.com/send?phone={formatted_phone.replace("+", "")}'
                logger.info('[DEBUG] URL before navigation: %s', driver.current_url)
                logger.info('[DEBUG] Opening chat URL: %s', whatsapp_url)
                logger.info('[DEBUG] Phone number: %s', formatted_phone)
                
                # Use JavaScript navigation to avoid renderer timeout
                try:
                    driver.set_page_load_timeout(120)
                    driver.execute_script(f"window.location.href = '{whatsapp_url}'")
                    logger.info('[DEBUG] JavaScript navigation executed')
                except Exception as nav_error:
                    logger.warning('[DEBUG] JavaScript navigation exception: %s', nav_error)
                
                # Wait a moment for URL to change
                time.sleep(1)
                logger.info('[DEBUG] URL after navigation: %s', driver.current_url)
                
                # Wait for message composer to appear (not full page load)
                try:
                    logger.info('[DEBUG] Waiting for message composer or chat error')
                    WebDriverWait(driver, 15).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="conversation-panel-footer"] [contenteditable="true"]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="3"]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-footer"] [contenteditable="true"]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="intro-error"]')),
                            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "phone number isn\'t on WhatsApp")]')),
                            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Phone number shared via url is invalid")]')),
                            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "blocked")]'))
                        )
                    )
                    logger.info('[DEBUG] Message composer or error detected')
                except Exception as e:
                    # Check if URL has changed despite timeout
                    current_url = driver.current_url
                    logger.info('[DEBUG] Current URL after timeout: %s', current_url)
                    if '/send?phone=' in current_url:
                        logger.info('[DEBUG] URL changed to chat despite timeout, continuing')
                    else:
                        error = f'Failed to load chat for {formatted_phone}: {e}'
                        logger.error('[DEBUG] Chat load failed: %s', error)
                        logger.error('[DEBUG] Traceback: %s', traceback.format_exc())
                        _take_screenshot(driver, f'chat_load_fail_{formatted_phone}')
                        _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                        return WhatsAppSendResult(
                            success=False,
                            phone_number=formatted_phone,
                            message_preview=preview,
                            error=error,
                        )
                
                # Check for various error conditions
                try:
                    page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
                    
                    # Phone number not on WhatsApp
                    if "phone number isn't on WhatsApp" in page_text or "phone number shared via url is invalid" in page_text:
                        error = 'Phone number is not on WhatsApp or invalid'
                        logger.error('WhatsApp send failed - %s', error)
                        _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                        return WhatsAppSendResult(
                            success=False,
                            phone_number=formatted_phone,
                            message_preview=preview,
                            error=error,
                        )
                    
                    # Blocked account
                    if "blocked" in page_text or "unable to send message" in page_text:
                        error = 'Account may be blocked or unable to send message'
                        logger.error('WhatsApp send failed - %s', error)
                        _take_screenshot(driver, f'blocked_{formatted_phone}')
                        _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                        return WhatsAppSendResult(
                            success=False,
                            phone_number=formatted_phone,
                            message_preview=preview,
                            error=error,
                        )
                    
                    # Check for intro-error element
                    try:
                        error_element = driver.find_element(By.CSS_SELECTOR, '[data-testid="intro-error"]')
                        if error_element:
                            error = 'Phone number is not on WhatsApp or chat unavailable'
                            logger.error('WhatsApp send failed - %s', error)
                            _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                            return WhatsAppSendResult(
                                success=False,
                                phone_number=formatted_phone,
                                message_preview=preview,
                                error=error,
                            )
                    except:
                        pass
                except Exception as e:
                    logger.warning('Error checking page text: %s', e)
                
                # Find message input box and type message
                try:
                    logger.info('[DEBUG] Looking for message input box')
                    logger.info('[DEBUG] Selectors: [data-testid="conversation-panel-footer"] [contenteditable="true"], div[contenteditable="true"][data-tab="3"], [data-testid="chat-footer"] [contenteditable="true"]')
                    
                    # Try multiple selectors for the message input
                    message_box = None
                    selectors_to_try = [
                        '[data-testid="conversation-panel-footer"] [contenteditable="true"]',
                        'div[contenteditable="true"][data-tab="3"]',
                        '[data-testid="chat-footer"] [contenteditable="true"]',
                        '[contenteditable="true"]'
                    ]
                    
                    for selector in selectors_to_try:
                        try:
                            message_box = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            logger.info('[DEBUG] Message box found with selector: %s', selector)
                            break
                        except:
                            continue
                    
                    if not message_box:
                        raise Exception('Message input box not found with any selector')
                    
                    logger.info('[DEBUG] Clicking message box')
                    message_box.click()
                    time.sleep(0.5)  # Wait for focus
                    
                    logger.info('[DEBUG] Typing message: %r', clean_msg[:50])
                    message_box.clear()  # Clear any existing text
                    message_box.send_keys(clean_msg)
                    time.sleep(0.5)  # Wait for text to appear
                    
                    # Verify that text was actually typed
                    current_text = message_box.get_attribute('textContent') or message_box.get_attribute('innerText') or ''
                    logger.info('[DEBUG] Textbox content after typing: %r', current_text[:50])
                    
                    if not current_text or clean_msg[:20] not in current_text:
                        error = f'Message not typed in textbox. Expected: {clean_msg[:20]}, Got: {current_text[:20]}'
                        logger.error('[DEBUG] Message typing verification failed: %s', error)
                        logger.error('[DEBUG] Selector used: %s', selector)
                        
                        # Save DOM source for debugging
                        try:
                            dom_file = os.path.join(_SCREENSHOT_DIR, f'typing_fail_dom_{formatted_phone}.html')
                            with open(dom_file, 'w', encoding='utf-8') as f:
                                f.write(driver.page_source)
                            logger.info('[DEBUG] Saved DOM source to %s', dom_file)
                        except Exception as dom_error:
                            logger.error('[DEBUG] Failed to save DOM source: %s', dom_error)
                        
                        _take_screenshot(driver, f'message_type_fail_{formatted_phone}')
                        _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                        return WhatsAppSendResult(
                            success=False,
                            phone_number=formatted_phone,
                            message_preview=preview,
                            error=error,
                        )
                    
                    logger.info('[DEBUG] Message typed and verified successfully')
                except Exception as e:
                    error = f'Failed to type message: {e}'
                    logger.error('[DEBUG] Message typing failed: %s', error)
                    logger.error('[DEBUG] Traceback: %s', traceback.format_exc())
                    
                    # Save DOM source on failure
                    try:
                        dom_file = os.path.join(_SCREENSHOT_DIR, f'typing_exception_dom_{formatted_phone}.html')
                        with open(dom_file, 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        logger.info('[DEBUG] Saved DOM source to %s', dom_file)
                    except Exception as dom_error:
                        logger.error('[DEBUG] Failed to save DOM source: %s', dom_error)
                    
                    _take_screenshot(driver, f'message_type_fail_{formatted_phone}')
                    _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                    return WhatsAppSendResult(
                        success=False,
                        phone_number=formatted_phone,
                        message_preview=preview,
                        error=error,
                    )
                
                # Find and click Send button (with ENTER fallback)
                try:
                    logger.info('[DEBUG] Looking for Send button')
                    logger.info('[DEBUG] Selectors: [data-testid="send"], [data-testid="send-icon"]')
                    
                    send_button = None
                    send_selectors = [
                        '[data-testid="send"]',
                        '[data-testid="send-icon"]',
                        'button[data-testid="send"]',
                        'span[data-icon="send"]'
                    ]
                    
                    for selector in send_selectors:
                        try:
                            send_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            logger.info('[DEBUG] Send button found with selector: %s', selector)
                            break
                        except:
                            continue
                    
                    if send_button:
                        logger.info('[DEBUG] Clicking Send button')
                        send_button.click()
                        logger.info('[DEBUG] Send button clicked')
                    else:
                        # Fallback: press ENTER to send
                        logger.info('[DEBUG] Send button not found, using ENTER key fallback')
                        message_box.send_keys(Keys.RETURN)
                        logger.info('[DEBUG] ENTER key pressed')
                        time.sleep(0.5)
                        
                except Exception as e:
                    # Try ENTER as fallback if click failed
                    logger.warning('[DEBUG] Send button click failed: %s', e)
                    logger.info('[DEBUG] Trying ENTER key fallback')
                    try:
                        message_box.send_keys(Keys.RETURN)
                        logger.info('[DEBUG] ENTER key pressed as fallback')
                        time.sleep(0.5)
                    except Exception as enter_error:
                        error = f'Failed to send message (click and ENTER both failed): {e} | ENTER error: {enter_error}'
                        logger.error('[DEBUG] Send failed: %s', error)
                        logger.error('[DEBUG] Traceback: %s', traceback.format_exc())
                        _take_screenshot(driver, f'send_click_fail_{formatted_phone}')
                        _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                        return WhatsAppSendResult(
                            success=False,
                            phone_number=formatted_phone,
                            message_preview=preview,
                            error=error,
                        )
                
                # Wait for NEW message to appear in chat (confirmation)
                try:
                    logger.info('[DEBUG] Waiting for outgoing message element')
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="msg-out"]'))
                    )
                    logger.info('[DEBUG] Outgoing message element detected')
                    
                    # Verify the message contains our text
                    logger.info('[DEBUG] Verifying message content')
                    time.sleep(1)
                    messages = driver.find_elements(By.CSS_SELECTOR, '[data-testid="msg-out"]')
                    logger.info('[DEBUG] Found %d outgoing messages', len(messages))
                    message_found = False
                    
                    for msg in messages:
                        try:
                            msg_text = msg.text
                            logger.info('[DEBUG] Checking message: %r', msg_text[:50])
                            if clean_msg[:30] in msg_text:
                                message_found = True
                                logger.info('[DEBUG] Message content matched!')
                                break
                        except:
                            continue
                    
                    if not message_found:
                        error = 'Message sent but could not verify content in chat'
                        logger.error('[DEBUG] Message verification failed: %s', error)
                        logger.error('[DEBUG] Expected snippet: %r', clean_msg[:30])
                        _take_screenshot(driver, f'verification_fail_{formatted_phone}')
                        _append_send_log(f'{datetime.now().isoformat()} | UNVERIFIED | {formatted_phone} | {error}')
                        return WhatsAppSendResult(
                            success=False,
                            phone_number=formatted_phone,
                            message_preview=preview,
                            error=error,
                        )
                    else:
                        logger.info('[DEBUG] Message verification successful')
                        
                except Exception as e:
                    error = f'Message send confirmation failed: {e}'
                    logger.error('[DEBUG] Message confirmation failed: %s', error)
                    logger.error('[DEBUG] Traceback: %s', traceback.format_exc())
                    _take_screenshot(driver, f'confirmation_fail_{formatted_phone}')
                    _append_send_log(f'{datetime.now().isoformat()} | UNVERIFIED | {formatted_phone} | {error}')
                    return WhatsAppSendResult(
                        success=False,
                        phone_number=formatted_phone,
                        message_preview=preview,
                        error=error,
                    )
                
                logger.info('[DEBUG] WhatsApp send verified successfully | to=%s | session=%s', formatted_phone, ADMIN_WHATSAPP_NUMBER)
                _append_send_log(f'{datetime.now().isoformat()} | SENT | {formatted_phone} | verified=yes')
                result = WhatsAppSendResult(
                    success=True,
                    phone_number=formatted_phone,
                    message_preview=preview,
                    verified_in_log=True,
                )
                logger.info('[DEBUG] Returning success=True from send_whatsapp_message')
                return result
                
            except Exception as exc:
                error = str(exc)
                logger.exception('WhatsApp send failed | to=%s | error=%s', formatted_phone, error)
                _take_screenshot(driver if 'driver' in locals() else None, f'exception_{formatted_phone}')
                
                # Check if it's a driver crash
                if 'chrome not reachable' in error.lower() or 'session deleted' in error.lower() or 'target frame detached' in error.lower():
                    logger.warning('Driver crash detected, reinitializing...')
                    _handle_driver_crash()
                    if attempt < _MAX_RETRIES:
                        logger.info('Retrying after crash (attempt %d/%d)', attempt + 1, _MAX_RETRIES)
                        time.sleep(_RETRY_DELAY)
                        continue
                
                _append_send_log(f'{datetime.now().isoformat()} | FAILED | {formatted_phone} | {error}')
                return WhatsAppSendResult(
                    success=False,
                    phone_number=formatted_phone,
                    message_preview=preview,
                    error=error,
                )
    
    # Should not reach here, but if all retries exhausted
    error = f'Failed after {_MAX_RETRIES + 1} attempts'
    logger.error('WhatsApp send failed - %s', error)
    return WhatsAppSendResult(
        success=False,
        phone_number=formatted_phone,
        message_preview=preview,
        error=error,
    )


def send_admin_notification(message_type: str, student_name: str, phone_number: str, message_sent: str) -> WhatsAppSendResult:
    """Send a copy of the outbound message to the admin WhatsApp number."""
    admin_message = f"""Pillay Sir's ICSE Classes - WhatsApp Message Sent

Message Type: {message_type.upper()}
Student: {student_name}
Sent To: {phone_number}
Session Number: {ADMIN_WHATSAPP_NUMBER}
Timestamp: {datetime.now().strftime('%d %B %Y, %I:%M %p')}

Message Content:
{message_sent}

---
This is an automated notification from the WhatsApp Reminder System."""

    result = send_whatsapp_message(ADMIN_WHATSAPP_NUMBER, admin_message, wait_time=12)
    if result.success:
        logger.info('Admin notification sent for %s -> %s', student_name, phone_number)
    else:
        logger.warning('Admin notification failed for %s -> %s: %s', student_name, phone_number, result.error)
    return result


def send_admin_summary(summary_message: str) -> Optional[WhatsAppSendResult]:
    """
    Send a summary message to the admin WhatsApp number.

    This is wrapped in an independent try/except so that summary failures
    never affect the main message processing queue.
    """
    try:
        result = send_whatsapp_message(ADMIN_WHATSAPP_NUMBER, summary_message, wait_time=10)
        if result.success:
            logger.info('Admin summary sent successfully')
        else:
            logger.warning('Admin summary failed: %s', result.error)
        return result
    except Exception as exc:
        logger.exception('Admin summary exception: %s', exc)
        return None


def _take_screenshot(driver, context: str):
    """Take a screenshot for debugging purposes."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = os.path.join(_SCREENSHOT_DIR, f'{context}_{timestamp}.png')
        driver.save_screenshot(screenshot_path)
        logger.info('Screenshot saved: %s', screenshot_path)
    except Exception as e:
        logger.error('Failed to take screenshot: %s', e)


def _handle_driver_crash():
    """Handle driver crash by reinitializing."""
    global _driver_instance
    logger.warning('Driver crash detected, reinitializing...')
    try:
        close_driver()
    except Exception as e:
        logger.error('Error during crash cleanup: %s', e)
    _driver_instance = None


def cleanup_whatsapp_session():
    """
    Clean up WhatsApp session by closing the browser.
    Call this after completing a batch of messages.
    """
    try:
        close_driver()
    except Exception as e:
        logger.error('Error during session cleanup: %s', e)
        # Force cleanup even on error
        global _driver_instance
        _driver_instance = None
        _release_profile_lock()
