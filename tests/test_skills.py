from skills import SKILL_KEYWORDS, extract_skills


def test_has_at_least_40_skills() -> None:
    assert len(SKILL_KEYWORDS) >= 40


def test_basic_extraction_sorted_and_deduplicated() -> None:
    text = "We use Python, python3, and TypeScript with React on AWS."
    assert extract_skills(text) == ["AWS", "Python", "React", "TypeScript"]


def test_symbol_skills() -> None:
    assert extract_skills("Experience with C++ and C# and .NET") == [".NET", "C#", "C++"]


def test_java_does_not_match_javascript() -> None:
    assert extract_skills("Strong JavaScript skills") == ["JavaScript"]
    assert "Java" in extract_skills("Java and JavaScript")


def test_aliases_map_to_canonical_name() -> None:
    skills = extract_skills("Postgres, k8s, golang, node.js, nextjs, machine-learning")
    assert skills == ["Go", "Kubernetes", "Machine Learning", "Next.js", "Node.js", "PostgreSQL"]


def test_postgresql_does_not_imply_sql_and_rest_is_not_a_word_match() -> None:
    assert extract_skills("PostgreSQL experience, and the rest of the team") == ["PostgreSQL"]
    assert "REST" in extract_skills("Design RESTful services")


def test_no_skills_in_empty_or_irrelevant_text() -> None:
    assert extract_skills("") == []
    assert extract_skills("Great communication and teamwork") == []
