#!/usr/bin/env python3
"""
Gate 0 Runtime Route-Guard Test

Proves at runtime (no network) that with Analyzer Mode on:
- The Fyers order function is never called for placeorder, placesmartorder,
  basketorder, splitorder
- The sandbox function IS called instead

And with Analyzer Mode off:
- The Fyers order function IS called (negative control proving the test can
  detect a live call)

Run from vendor/openalgo directory:
    cd vendor/openalgo && uv run python ../../scripts/gate0_guard_check.py
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# =============================================================================
# ISOLATION: Set up temp databases and dummy env vars BEFORE any vendor imports
# =============================================================================

# Create a temp directory for all databases
_temp_dir = tempfile.mkdtemp(prefix="gate0_guard_")
os.environ["DATABASE_URL"] = f"sqlite:///{_temp_dir}/openalgo.db"
os.environ["SANDBOX_DATABASE_URL"] = f"sqlite:///{_temp_dir}/sandbox.db"
os.environ["LATENCY_DATABASE_URL"] = f"sqlite:///{_temp_dir}/latency.db"
os.environ["LOGS_DATABASE_URL"] = f"sqlite:///{_temp_dir}/logs.db"
os.environ["HEALTH_DATABASE_URL"] = f"sqlite:///{_temp_dir}/health.db"
os.environ["HISTORIFY_DATABASE_URL"] = f"{_temp_dir}/historify.duckdb"

# Required env vars for auth_db (fail-fast if missing)
os.environ["API_KEY_PEPPER"] = "a" * 64  # 64 hex chars = 32 bytes
os.environ["FERNET_SALT"] = "b" * 64
os.environ["SMTP_KEY_SALT"] = "smtp-test-salt"

# Other required env vars
os.environ["BROKER_API_KEY"] = "test_broker_key"
os.environ["BROKER_API_SECRET"] = "test_broker_secret"
os.environ["APP_KEY"] = "c" * 64
os.environ["VALID_BROKERS"] = "fyers"
os.environ["FLASK_HOST_IP"] = "127.0.0.1"
os.environ["FLASK_PORT"] = "5000"
os.environ["FLASK_DEBUG"] = "False"
os.environ["FLASK_ENV"] = "development"
os.environ["HOST_SERVER"] = "http://127.0.0.1:5000"
os.environ["NGROK_ALLOW"] = "FALSE"

# Add vendor/openalgo to sys.path - find it dynamically
# The script can be run from vendor/openalgo:
#   cd vendor/openalgo && python ../../scripts/gate0_guard_check.py
# Or from repo root: python scripts/gate0_guard_check.py
# In the worktree, vendor is in the main GitHub checkout.
# On CI, vendor is cloned into repo root.
_script_path = Path(__file__).resolve()

# Check if we're in vendor/openalgo by looking for database/ directory
if (_script_path.parent.parent / "database").exists():
    # Running from vendor/openalgo directory
    _vendor_path = _script_path.parent.parent
else:
    # Running from repo root, check for vendor/openalgo in repo root (CI case)
    _vendor_path = _script_path.parent.parent / "vendor" / "openalgo"
    if not _vendor_path.exists():
        # Fall back to main GitHub checkout (local worktree case)
        _vendor_path = Path("/Users/suryavamsipichika/GitHub/Pulse/vendor/openalgo")

sys.path.insert(0, str(_vendor_path))

# =============================================================================
# NOW import vendor modules (after env vars are set)
# =============================================================================

# Initialize databases (imports after env vars set - required for isolation)
from database.auth_db import init_db as init_auth_db  # noqa: E402
from database.sandbox_db import init_db as init_sandbox_db  # noqa: E402
from database.settings_db import init_db as init_settings_db  # noqa: E402

init_auth_db()
init_settings_db()
init_sandbox_db()

# Mock restx_api.schemas before importing services to avoid circular import
# Create a mock OrderSchema
mock_order_schema = MagicMock()
mock_order_schema.load = lambda data: data

# Mock the restx_api.schemas module
sys.modules["restx_api.schemas"] = MagicMock()
sys.modules["restx_api.schemas"].OrderSchema = lambda: mock_order_schema

# Also mock restx_api and its submodules to avoid circular imports
sys.modules["restx_api"] = MagicMock()
sys.modules["restx_api.options_multiorder"] = MagicMock()
sys.modules["restx_api.options_multiorder.api"] = MagicMock()
sys.modules["services.options_multiorder_service"] = MagicMock()

# Import the services we need to test - import inside functions to avoid
# circular imports. We'll import them lazily in the test functions.

# =============================================================================
# TEST HARNESS
# =============================================================================

# Track calls
call_log = {
    "fyers_place_order_api": 0,
    "fyers_place_smartorder_api": 0,
    "sandbox_place_order": 0,
    "sandbox_place_smart_order": 0,
}


def reset_call_log():
    for k in call_log:
        call_log[k] = 0


def mock_fyers_place_order_api(*args, **kwargs):
    call_log["fyers_place_order_api"] += 1
    # Return a mock response like the real function
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.status_code = 200
    return mock_resp, {"s": "ok", "id": "test_order_id"}, "test_order_id"


def mock_fyers_place_smartorder_api(*args, **kwargs):
    call_log["fyers_place_smartorder_api"] += 1
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.status_code = 200
    return mock_resp, {"s": "ok", "id": "test_smart_order_id"}, "test_smart_order_id"


def mock_sandbox_place_order(*args, **kwargs):
    call_log["sandbox_place_order"] += 1
    return True, {"status": "success", "orderid": "sandbox_order_id", "mode": "analyze"}, 200


def mock_sandbox_place_smart_order(*args, **kwargs):
    call_log["sandbox_place_smart_order"] += 1
    return True, {"status": "success", "orderid": "sandbox_smart_order_id", "mode": "analyze"}, 200


def mock_get_auth_token_broker(api_key):
    return "test_auth_token", "fyers"


def mock_verify_api_key(api_key):
    return "test_user_id"


def mock_get_analyze_mode():
    # This will be overridden per test case
    return getattr(mock_get_analyze_mode, "_value", True)


# Patch the analyze mode getter (import after env vars - required for isolation)
import database.settings_db  # noqa: E402

database.settings_db.get_analyze_mode = mock_get_analyze_mode

# Patch the auth functions (import after env vars - required for isolation)
import database.auth_db  # noqa: E402

database.auth_db.get_auth_token_broker = mock_get_auth_token_broker
database.auth_db.verify_api_key = mock_verify_api_key


# =============================================================================
# TEST CASES
# =============================================================================


def run_case(
    case_name,
    analyzer_on,
    order_func_name,
    order_data,
    expected_sandbox,
    expected_fyers,
    api_key,
):
    """Run a single test case and return result dict."""
    reset_call_log()
    mock_get_analyze_mode._value = analyzer_on

    # Import services lazily to avoid circular imports
    if order_func_name == "place_order":
        from services.place_order_service import place_order as order_func
    elif order_func_name == "place_smart_order":
        from services.place_smart_order_service import place_smart_order as order_func
    elif order_func_name == "place_basket_order":
        from services.basket_order_service import place_basket_order as order_func
    elif order_func_name == "split_order":
        from services.split_order_service import split_order as order_func
    else:
        raise ValueError(f"Unknown order function: {order_func_name}")

    # Apply patches for this case
    with (
        patch("services.sandbox_service.sandbox_place_order", mock_sandbox_place_order),
        patch(
            "services.sandbox_service.sandbox_place_smart_order",
            mock_sandbox_place_smart_order,
        ),
        patch("broker.fyers.api.order_api.place_order_api", mock_fyers_place_order_api),
        patch(
            "broker.fyers.api.order_api.place_smartorder_api",
            mock_fyers_place_smartorder_api,
        ),
    ):
        try:
            success, response, status_code = order_func(order_data, api_key=api_key)
            observed_sandbox = (
                call_log["sandbox_place_order"] + call_log["sandbox_place_smart_order"]
            )
            observed_fyers = (
                call_log["fyers_place_order_api"] + call_log["fyers_place_smartorder_api"]
            )
        except Exception as e:
            return {
                "case": case_name,
                "expected": f"sandbox={expected_sandbox}, fyers={expected_fyers}",
                "observed": f"ERROR: {e}",
                "ok": False,
            }

    ok = (observed_sandbox == expected_sandbox) and (observed_fyers == expected_fyers)
    return {
        "case": case_name,
        "expected": f"sandbox={expected_sandbox}, fyers={expected_fyers}",
        "observed": f"sandbox={observed_sandbox}, fyers={observed_fyers}",
        "ok": ok,
    }


def main():
    # Create a test API key
    test_api_key = "test_api_key_123"

    # Base order data for NSE RELIANCE BUY 1 MIS MARKET
    base_order = {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "action": "BUY",
        "quantity": 1,
        "pricetype": "MARKET",
        "product": "MIS",
        "strategy": "test_strategy",
    }

    # Smart order data
    smart_order = {
        **base_order,
        "position_size": 0,
    }

    # Basket order data (one order)
    basket_order = {
        "apikey": test_api_key,
        "strategy": "test_strategy",
        "orders": [base_order],
    }

    # Split order data
    split_order = {
        **base_order,
        "total_quantity": 1,
        "splitsize": 1,
    }

    results = []

    # Case 1: Analyzer ON, placeorder
    results.append(
        run_case(
            "analyzer_on_placeorder",
            analyzer_on=True,
            order_func_name="place_order",
            order_data=base_order,
            expected_sandbox=1,
            expected_fyers=0,
            api_key=test_api_key,
        )
    )

    # Case 2: Analyzer ON, placesmartorder
    results.append(
        run_case(
            "analyzer_on_placesmartorder",
            analyzer_on=True,
            order_func_name="place_smart_order",
            order_data=smart_order,
            expected_sandbox=1,
            expected_fyers=0,
            api_key=test_api_key,
        )
    )

    # Case 3: Analyzer ON, basketorder with one order
    results.append(
        run_case(
            "analyzer_on_basketorder",
            analyzer_on=True,
            order_func_name="place_basket_order",
            order_data=basket_order,
            expected_sandbox=1,
            expected_fyers=0,
            api_key=test_api_key,
        )
    )

    # Case 4: Analyzer ON, splitorder
    results.append(
        run_case(
            "analyzer_on_splitorder",
            analyzer_on=True,
            order_func_name="split_order",
            order_data=split_order,
            expected_sandbox=1,
            expected_fyers=0,
            api_key=test_api_key,
        )
    )

    # Case 5: Analyzer OFF, placeorder (negative control - MUST call Fyers)
    results.append(
        run_case(
            "analyzer_off_placeorder_negative_control",
            analyzer_on=False,
            order_func_name="place_order",
            order_data=base_order,
            expected_sandbox=0,
            expected_fyers=1,
            api_key=test_api_key,
        )
    )

    # Print results as JSON lines
    all_ok = True
    for r in results:
        print(json.dumps(r))
        if not r["ok"]:
            all_ok = False

    # Exit with error code if any case failed
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
