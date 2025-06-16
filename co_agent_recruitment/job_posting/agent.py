from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent as PydanticAgent
from google.adk.agents import Agent
from datetime import datetime

class KeySkills(BaseModel):
    programming_languages: Optional[List[str]] = Field(
        None, description="A list of programming languages."
    )
    frameworks_libraries: Optional[List[str]] = Field(
        None, description="A list of frameworks and libraries."
    )
    databases: Optional[List[str]] = Field(
        None, description="A list of databases."
    )
    cloud_platforms: Optional[List[str]] = Field(
        None, description="A list of cloud platforms."
    )
    tools_technologies: Optional[List[str]] = Field(
        None, description="A list of other tools and technologies."
    )
class Education(BaseModel):
    institution: str = Field(..., description="The name of the institution.")
    degree: Optional[str] = Field(None, description="The degree obtained.")
    field_of_study: Optional[str] = Field(
        None, description="The field of study."
    )

class Location(BaseModel):
    city: Optional[str] = Field(None, description='The city or cities where the job is located.')
    state: Optional[str] = Field(None, description='The state or region where the job is located.')
    countryCode: Optional[str] = Field(None, description='code as per ISO-3166-1 ALPHA-2, e.g. US, AU, IN')
    remote: Optional[bool] = Field(None, description='Whether the job is remote or not')

class HiringOrg(BaseModel):
    description: Optional[str] = Field(None, description="A brief description of the company.")
    name: Optional[str] = Field(None, description="The name of the company.")
    website_url: Optional[str] = Field(None, description="The URL of the company's website.")
    application_email: Optional[str] = Field(None, description="The email address for job applications.")
class BaseSalary(BaseModel):
    amount: Optional[float] = Field(None, description="The base salary amount.")
    currency: Optional[str] = Field(None, description="The currency of the salary amount, e.g., USD, EUR.")
    unit: Optional[str] = Field(None, description="The unit of the salary, e.g., per year, per month, per hour.")
    description: Optional[str] = Field(None, description="A brief description of the salary structure.")
class JobPosting(BaseModel): 
    job_title: str = Field(..., description="The job title or role.")
    company: HiringOrg = Field(None, description="The company details, including name and description.")
    location: Location = Field(..., description="The location of the job.")
    years_of_experience: Optional[str] = Field(None, description="The number of years of experience required. Mention + or - if applicable, e.g., 3+ years, 5-7 years.")
    key_responsibilities: List[str] = Field(..., description="A list of key responsibilities for the role. List main 10 responsibilities in bullet points briefly.")
    required_skills: KeySkills = Field(..., description="A list of key skills required for the role.")
    required_qualifications: Optional[List[Education]] = Field(None, description="A list of qualifications required for the role.")
    industry_type: Optional[str] = Field(..., description="The industry type or sector for the job. eg Manufacturing, IT, Finance, Mortgage, Insurance etc.")
    salary_range: Optional[str] = Field(None, description="The salary range for the job, if available.")
    base_salary: Optional[BaseSalary] = Field(None, description="The base salary for the job, if available.")
    type_of_employment: Optional[str] = Field(None, description="The type of employment, e.g., Full-time, Part-time, Contract, Internship.")
    date_posted: Optional[str] = Field(None, description="The date when the job was posted.")
    validThrough: Optional[datetime] = Field(None, description="The date and time until which the job posting is valid. Format: ISO 8601.")
    
async def analyze_job_posting(job_posting: str) -> Dict:
    """Analyzes unstructured job posting text and returns a structured JSON object.

    Args:
        job_posting(str): The unstructured text content of a job posting.

    Returns:
        dict: A structured JSON object containing key information about the job posting.
    """
 
    agent = PydanticAgent(
        "gemini-2.5-flash-preview-05-20",
        instructions="You are parser that reads job postings. Your task is to transform the unstructured job posting text provided below into a single, structured, and comprehensive JSON object ",
    )
    try:
        result = await agent.run(job_posting, output_type=JobPosting)
        return result.output.model_dump(exclude_none=True)
    except ValidationError as e:
        # Log the error or handle it as needed
        error_messages = []
        for error in e.errors():
            error_messages.append(f"Field: {error.get('loc', 'N/A')}, Type: {error.get('type', 'N/A')}, Message: {error.get('msg', 'N/A')}")
        return {
            "error": "Pydantic validation failed during job posting analysis.",
            "details": error_messages
        }
    except Exception as e:
        # Catch any other unexpected errors from the agent.run call
        return {
            "error": "An unexpected error occurred during job posting analysis.",
            "details": str(e)
        }
   
job_posting_agent = Agent(
    name="job_posting_agent",
    model="gemini-2.5-flash-preview-05-20",
    description="Agent to parse job posting text and transform it into a structured, comprehensive JSON object.",
    instruction="You are parser that reads job postings. Your task is to transform the unstructured job posting text provided below into a single, structured, and comprehensive JSON object ",
    tools=[analyze_job_posting]#, resume_agent]
)

#root_agent = job_posting_agent