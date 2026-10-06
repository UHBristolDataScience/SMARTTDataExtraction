import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


PAGE_PATH = (
    Path(__file__).parents[1] / "application" / "pages" / "choose_data_source.py"
)


class SessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        self.session_state = SessionState()
        self.source = "ICCA"
        self.server = "synthetic_server"
        self.database = "synthetic_database"
        self.clicked_button = None
        self.button_disabled = {}
        self.error = MagicMock()
        self.success = MagicMock()
        self.switch_page = MagicMock()

    def write(self, *args, **kwargs):
        pass

    def title(self, *args, **kwargs):
        pass

    def header(self, *args, **kwargs):
        pass

    def markdown(self, *args, **kwargs):
        pass

    def selectbox(self, *args, **kwargs):
        return self.source

    def text_input(self, label, *args, **kwargs):
        if "Server" in label:
            return self.server
        if "database name" in label:
            return self.database
        raise AssertionError(f"Unexpected text input: {label}")

    def button(self, label, *args, **kwargs):
        disabled = kwargs.get("disabled", False)
        self.button_disabled[label] = disabled
        return label == self.clicked_button and not disabled


def render_page(st, run_query):
    fake_utilities = types.ModuleType("utilities")
    fake_utilities.run_query = run_query
    fake_utilities._hide_pages = MagicMock()

    fake_switch_page_module = types.ModuleType(
        "streamlit_extras.switch_page_button"
    )
    fake_switch_page_module.switch_page = MagicMock()
    fake_streamlit_extras = types.ModuleType("streamlit_extras")

    module_name = f"choose_data_source_under_test_{id(st)}_{run_query.call_count}"
    spec = importlib.util.spec_from_file_location(module_name, PAGE_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(
        sys.modules,
        {
            "streamlit": st,
            "streamlit_extras": fake_streamlit_extras,
            "streamlit_extras.switch_page_button": fake_switch_page_module,
            "utilities": fake_utilities,
        },
    ):
        spec.loader.exec_module(module)


class ConnectionPage(unittest.TestCase):
    def test_successful_validation_enables_continue(self):
        st = FakeStreamlit()
        run_query = MagicMock(return_value=[object()])

        st.clicked_button = "Test Connection"
        render_page(st, run_query)

        self.assertFalse(st.session_state["continue_disabled"])
        self.assertEqual(
            {
                "server": "synthetic_server",
                "database": "synthetic_database",
            },
            st.session_state["icca_config"],
        )
        run_query.assert_called_once()

    def test_test_then_continue(self):
        st = FakeStreamlit()
        run_query = MagicMock(return_value=[object()])

        st.clicked_button = "Test Connection"
        render_page(st, run_query)
        st.clicked_button = "Continue"
        render_page(st, run_query)

        st.switch_page.assert_called_once_with("pages/choose_schema.py")
        run_query.assert_called_once()

    def test_changed_inputs_require_revalidation(self):
        st = FakeStreamlit()
        run_query = MagicMock(return_value=[object()])

        st.clicked_button = "Test Connection"
        render_page(st, run_query)
        st.server = "changed_synthetic_server"
        st.clicked_button = "Continue"
        render_page(st, run_query)

        self.assertTrue(st.button_disabled["Continue"])
        st.switch_page.assert_not_called()
        run_query.assert_called_once()

    def test_changed_source_requires_revalidation(self):
        st = FakeStreamlit()
        run_query = MagicMock(return_value=[object()])

        st.clicked_button = "Test Connection"
        render_page(st, run_query)
        st.source = "MIMIC-IV"
        st.clicked_button = "Continue"
        render_page(st, run_query)

        self.assertTrue(st.session_state["continue_disabled"])
        self.assertIsNone(
            st.session_state.get("connection_validation_receipt")
        )
        self.assertNotIn("icca_config", st.session_state)
        st.switch_page.assert_not_called()
        run_query.assert_called_once()

    def test_failed_retest_cannot_reuse_success(self):
        st = FakeStreamlit()
        run_query = MagicMock(return_value=[object()])

        st.clicked_button = "Test Connection"
        render_page(st, run_query)

        def fail_after_checking_invalidation(*args, **kwargs):
            self.assertIsNone(
                st.session_state.get("connection_validation_receipt")
            )
            self.assertNotIn("icca_config", st.session_state)
            raise RuntimeError("SYNTHETIC_FAILURE_MARKER")

        run_query.side_effect = fail_after_checking_invalidation
        st.clicked_button = "Test Connection"
        render_page(st, run_query)

        rendered_errors = " ".join(
            call.args[0] for call in st.error.call_args_list
        )
        self.assertNotIn("SYNTHETIC_FAILURE_MARKER", rendered_errors)
        self.assertTrue(st.session_state["continue_disabled"])
        self.assertIsNone(
            st.session_state.get("connection_validation_receipt")
        )
        self.assertNotIn("icca_config", st.session_state)
        self.assertEqual(2, run_query.call_count)


if __name__ == "__main__":
    unittest.main()
