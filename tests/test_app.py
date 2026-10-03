import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


APP_PATH = Path(__file__).parents[1] / "application" / "app.py"


class SessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class FakeStreamlit(types.ModuleType):
    def __init__(self, *, selected_project=None, project_name=None):
        super().__init__("streamlit")
        self.selected_project = selected_project
        self.project_name = project_name
        self.session_state = SessionState()
        self.sidebar = types.SimpleNamespace(markdown=MagicMock())
        self.error = MagicMock()
        self.switch_page = MagicMock()

    def title(self, *args, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass

    def markdown(self, *args, **kwargs):
        pass

    def selectbox(self, *args, **kwargs):
        return self.selected_project

    def text_input(self, *args, **kwargs):
        return self.project_name

    def button(self, *args, **kwargs):
        return True


def load_app(*, selected_project=None, project_name=None):
    fake_streamlit = FakeStreamlit(
        selected_project=selected_project,
        project_name=project_name,
    )
    wrapper = MagicMock(name="LocalDatabaseWrapper")
    fake_utilities = types.ModuleType("utilities")
    fake_utilities.run_query = MagicMock()
    fake_utilities._hide_pages = MagicMock()
    fake_utilities.LocalDatabaseWrapper = wrapper

    module_name = f"sniffer_app_under_test_{id(fake_streamlit)}"
    spec = importlib.util.spec_from_file_location(module_name, APP_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(
        sys.modules,
        {
            "streamlit": fake_streamlit,
            "utilities": fake_utilities,
            "pandas": types.ModuleType("pandas"),
        },
    ):
        spec.loader.exec_module(module)

    module.glob = MagicMock(return_value=["../data/existing_project.db"])
    return module, fake_streamlit, wrapper


class ProjectPage(unittest.TestCase):
    def test_ambiguous_choice_does_not_open_store(self):
        app, st, wrapper = load_app(
            selected_project="existing_project",
            project_name="new_project",
        )

        app.name_project()

        wrapper.assert_not_called()
        st.switch_page.assert_not_called()
        st.error.assert_called_once()
        self.assertIn("either", st.error.call_args.args[0].lower())

    def test_invalid_new_name_never_reaches_wrapper(self):
        invalid_names = (
            "",
            "   ",
            ".",
            "..",
            "parent/child",
            "parent\\child",
            "CON",
            "con.notes",
            "COM1",
            "LPT9.log",
            "trailing.",
            "trailing ",
            "invalid:name",
            "control\x1fcharacter",
            "a" * 253,
            "\u00e9" * 127,
        )

        for invalid_name in invalid_names:
            with self.subTest(project_name=repr(invalid_name)):
                app, st, wrapper = load_app(project_name=invalid_name)

                app.name_project()

                wrapper.assert_not_called()
                st.switch_page.assert_not_called()
                st.error.assert_called_once()

    def test_existing_and_new_modes_route_consistently(self):
        cases = (
            (
                "existing_project",
                None,
                "existing_project.db",
                False,
                "pages/validate_old_project.py",
            ),
            (
                None,
                "new_project",
                "new_project.db",
                True,
                "pages/choose_data_source.py",
            ),
        )

        for selected, entered, filename, is_new, destination in cases:
            with self.subTest(selected=selected, entered=entered):
                app, st, wrapper = load_app(
                    selected_project=selected,
                    project_name=entered,
                )

                app.name_project()

                wrapper.assert_called_once()
                opened_path = wrapper.call_args.args[0]
                self.assertEqual(filename, opened_path.name)
                self.assertEqual(is_new, st.session_state["new_project"])
                st.switch_page.assert_called_once_with(destination)
                st.error.assert_not_called()


if __name__ == "__main__":
    unittest.main()
