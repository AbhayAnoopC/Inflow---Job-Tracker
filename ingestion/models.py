from pydantic import BaseModel


class Posting(BaseModel):
    external_id: str
    company_slug: str
    title: str
    location: str | None = None
    url: str | None = None
    # Used only locally for skill extraction; never stored in the DB.
    description: str | None = None
