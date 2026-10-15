import pytest

from filters import is_bc_location, is_coop


@pytest.mark.parametrize(
    "location",
    [
        "Vancouver, BC",
        "Victoria, British Columbia, Canada",
        "Remote",
        "remote - canada",
        "Burnaby",
        "KELOWNA, bc",
        "Surrey, BC (Hybrid)",
        "Richmond, BC",
    ],
)
def test_bc_locations_accepted(location: str) -> None:
    assert is_bc_location(location)


@pytest.mark.parametrize(
    "location",
    [
        None,
        "",
        "San Francisco, CA",
        "London, United Kingdom",
        "Toronto, ON",
        "Remote - US",
        "Remote (Europe)",
        "Abbotsford",  # BC city not in the list; documents current behavior
    ],
)
def test_non_bc_locations_rejected(location: str | None) -> None:
    assert not is_bc_location(location)


@pytest.mark.parametrize(
    "title",
    [
        "Software Engineer Intern",
        "Data Science Co-op (Spring 2027)",
        "Backend Coop Developer",
        "Software Developer, Co Op",
        "Student Developer",
        "New Grad Software Engineer",
        "Entry-Level QA Analyst",
        "Entry level Designer",
        "Junior Frontend Developer",
        "Engineering Internship",
    ],
)
def test_coop_titles_accepted(title: str) -> None:
    assert is_coop(title)


@pytest.mark.parametrize(
    "title",
    [
        "Senior Software Engineer",
        "Staff Product Designer",
        "Engineering Manager",
        "Internal Tools Engineer",  # "intern" must be a whole word
        "Principal Architect",
    ],
)
def test_coop_titles_rejected(title: str) -> None:
    assert not is_coop(title)
