import regex as re
import unicodedata
from typing import Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import logging

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def clean_text_to_ascii(
    text: str,
    remove_stopwords: bool = True,
    lemmatize: bool = True,
    min_word_length: int = 2
) -> Optional[str]:
    """
    Clean input text by removing special characters (except digits), converting to ASCII,
    optionally removing stopwords and lemmatizing words.

    Args:
        text (str): Input text to clean
        remove_stopwords (bool): Whether to remove stopwords (default: True)
        lemmatize (bool): Whether to lemmatize words (default: True)
        min_word_length (int): Minimum length of words to keep (default: 2)

    Returns:
        Optional[str]: Cleaned ASCII text or None if processing fails
    """
    try:
        # Ensure NLTK resources are available
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('punkt_tab')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)

        # Convert to lowercase and normalize unicode characters
        text = unicodedata.normalize('NFKD', text.lower())

        # Convert to ASCII, ignoring non-ASCII characters
        text = text.encode('ascii', 'ignore').decode('ascii')

        # Remove special characters (keep letters, digits, and spaces)
        text = re.sub(r'[^a-z0-9\s]', ' ', text)

        # Tokenize
        tokens = word_tokenize(text)

        # Remove short words
        tokens = [token for token in tokens if len(token) >= min_word_length]

        # Initialize lemmatizer
        if lemmatize:
            lemmatizer = WordNetLemmatizer()
            tokens = [lemmatizer.lemmatize(token) for token in tokens]

        # Remove stopwords
        if remove_stopwords:
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token not in stop_words]

        # Join tokens back into string
        cleaned_text = ' '.join(tokens)

        # Remove extra spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        return cleaned_text if cleaned_text else None

    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage
    sample_text = (
        "Hello, world! This is a test text with some special characters: ñ, é, ü."
    )
    cleaned_text = clean_text_to_ascii(sample_text)
    logger.info(cleaned_text)  # Output: "hello world test text special characters"
    sample_text2 = """
ROOPAL BANSAL



Senior Software Engineer at Xoriant
Bachelor of Engineering (Computer Science) with 8+ years of experience 

KEY SKILLS
CORE DEVELOPMENT  
CLIENT INTERACTION 
COORDINATION
TEAM PLAYER
IT SKILLS
•	Domain Knowledge: Manufacturing, Banking/Finance, Mortgage		PROFILE SUMMARY
Highly skilled Software Engineer with over 9 years of experience in the IT sector, specializing in Enterprise Applications, Business Process Analysis, API Design, and the development of core modules in Java and Python. Proven experience in managing microservices with NoSQL databases, utilizing design patterns with Java 8, and AWS service management using Terraform scripts. Adept at problem-solving, multi-tasking, and team collaboration. Proficient with OOP concepts, AWS EC2, ECS, S3, Lambda, and several other tools and platforms. Excellent communicator with a proven track record of successfully leading project teams and delivering high-quality software solutions.
•	Technologies and Framework: Core Java 8, J2EE, Spring Core,Spring Data, Spring Security, Spring Boot, Spring Cloud, Microservices, Hibernate, JPA, JDBC, Apache Camel, AWS, WebServices -REST, Splunk, Python, AWS
•	Database: 
MS-SQL , Oracle 10g, MongoDB, NoSql- Postgres, DynamoDB
•	Web Servers:
Tomcat Server, Putty 
•	Version Control:
Apache GIT, Tortoise SVN 
•	Development Tools: 
Eclipse, Intelli, STS, Jboss Developer Studio, Pycharm
•	Tools Used: Maven, Bamboo, Sonar, JIRA, SQL Server 2014 Management Studio, JMeter, HP QTP , SoapUI, PostMan, Squirrel 3.6, ActiveMQ, JIRA, Jenkins, RoboMongo
EDUCATION
B.E. (C.S.)  8.31 CGPA                 2014
I.T.M(Gwalior), RGPV University
12th   85.2%                                 2010
Carmel Convent School(CBSE)
10th   85.4%                                 2008
Carmel Convent School(CBSE)

INTERESTS 
Fitness, Swimming, Dancing, Playing Table Tennis, Badminton		ORGANISATIONAL EXPERIENCE

Senior Software Engineer | XORIANT | June 2020-Present
Project: EDIS – A Mortgage domain solution streamlining loan provision and document submission.
Technologies: Java 1.8+, Python, Spring Boot, AWS (EC2, dynamoDB, Redis, Step Function, Lambda, ECS, S3, Cloudwatch, SQS), Docker, Kafka basics, REST, Microservices
Tools: IntelliJ, Pycharm, Jenkins, Sonar, Git, Splunk, Kibana, AWS console, Maven, Terraform 0.13
Roles & Responsibility:
•	Design and implementation of complex APIs using Spring Boot, managing microservices with NoSQL databases.
•	Directed the design and architecture of an automated disclosures module, overseeing the project from business requirement gathering to product delivery.
•	Developed an event-based architecture for handling multiple events, processing data from queues.
•	Regularly utilized AWS services (EC2, ECS, Step function, Lambda), executing Python implementations, and maintained resources via Terraform scripts.
•	Mentored team members in task assignment and defect resolution.
•	Spearheaded the migration of swagger from SpringFox to OAPI 1.6.11 and Springboot upgrade from 2.4.13 to 2.6.9.
•	Handled production deployments independently and addressed production and higher environment deployment defects within SLAs.
•	Worked on security and vulnerability checks using Snyk, Sonar, Checkmarx, Twistlock, and Whitesource report.
•	Managed the development of features such as webhook notifications (event-driven), esigning, enote registration, delivery, and transfer, including automated registration (Mers eRegistry) and enote storage in eVault.
•	Utilized Redis for caching and Slf4j for logging.
•	Worked on additional projects including MDS, UPs, and Fulfillment.
•	Spearheaded the design and implementation of Spring Boot microservices, interacting with AWS S3 and persisting data using NoSQL MongoDB.
•	Facilitated the application of policies using Mulesoft, building code on AWS EC2 instances, and employing ECS for container orchestration.
•	Developed and executed Splunk queries for insightful reports.
•	Conducted software patches, exception handling, Swagger custom validations, and created Junits using Mockito.
•	Microservice upgrade from OB CMA 3.1.0 to CMA 3.1.2.
•	Managed deployments using Jenkins, ensuring seamless integration, testing, and product release.


Associate Consultant | CAPGEMINI | June 2018-May 2020

PSD2                                                                                                                                            
Payment Service Directive, an EU directive aiming to encourage market competition by obligating banks to expose APIs to third-party service providers.
Key Technologies: REST web services, JDK 1.8, Spring Boot, Microservices, MongoDB
Tools: STS, Jenkins, Sonar, Splunk, Git, Postman, RoboMongo, Amazon EC2, ECS, S3, Swagger, Bitbucket, Maven, Mule basics
Roles & Responsibility:
•	Engineered and implemented Spring Boot microservices, interacting with AWS S3, and employed MongoDB for data persistence.
•	Applied policies using Mulesoft, built code on AWS EC2 instances, and leveraged ECS for container orchestration.
•	Developed and executed Splunk queries for detailed reporting.
•	Created and executed Junits using Mockito for enhanced testing.
•	Managed software patches, exception handling, Swagger custom validations, and facilitated the microservices upgrade from OB CMA 3.1.0 to CMA 3.1.2.
•	Supervised deployments using Jenkins, ensuring successful integration, testing, and product release.

AVIVA - Customer                                                                         					
(An insurance domain offering a range of policies including life insurance, pensions, annuities, health insurance, and home insurance.)
Key Technologies: Java, REST web services, JDK 1.7, Spring, MS-SQL, Hibernate-JPA, Apache Camel, Spring Boot, Oracle 10g, Microservices
Tools: Jboss Developer Studio, Jboss Fuse 6.2.1, Jenkins, SonarQube, Splunk, Git, SoapUI, Swagger, SourceTree, Wiremock, Maven
Roles & Responsibility:
•	Successfully migrated API from Fuse 6.1 to Fuse 6.2.
•	Participated actively in user stories development, sprint planning, review, backlog refinement, and retrospective meetings following the Scrum framework.
•	Led deployments across various environments using Jenkins Job and pipeline, providing live deployment support including end-user assistance.
•	Managed UKDTs for building and installing OSGI bundles in Sprint, Runway, and Preprod environments.
•	Created Wiremock for existing 6.1 stub and addressed sonar issues reported by the customer.

Senior Software Engineer | INFOSYS | September 2014-May 2018

BVoC (Best View of Customer)                                      					
(An application designed to update and consolidate high-volume customer data from multiple sources for centralized storage and reporting.)
Technologies: Java, REST web services, JDK 1.7, JAXB, Spring basics, MS-SQL, Hibernate-JPA, Apache Camel
Tools: Eclipse, Tortoise SVN, Apache Tomcat, SQL Server 2014 Management Studio, SharePoint, WinSCP, IBM Websphere ActiveMQ, Putty, SonarQube, Git, Maven
Roles & Responsibility:
•	Analyzed business logics and independently implemented modules through JAX-RS.
•	Handled critical issues such as 'flipping', which involved client requirement gathering, DB design, documentation, and related implementations.
•	Managed bug-fixing, defect tracking for every release, and conducted source code reviews for peer developers.
•	Deployed code to different environments, including performing Unit and Integration testing in IT and QA environments.
•	Owned and delivered modules such as exception management in a timely manner.
•	Participated in project estimation activities.

VCD (Vehicle Control Database)                                                           				
(A web-based application for managing the availability of vehicles for testing purposes.) 
Technologies: Java, REST web services, JDK 1.7, Spring, Hibernate
Tools: Apache Maven, IntelliJ, Tortoise SVN, MS-SQL, Squirrel, SQL Server 2014 Management Studio, Sonar, SharePoint


Roles & Responsibility:
•	Developed core modules of the application independently using Java, Spring, and Hibernate, interacting with business and end users for key issues and requirement gathering.
•	Created UML class, sequence diagrams, and use cases for project structure using Microsoft Visio.
•	Followed a test-driven development process using Junit, fixed bugs in different modules in DEV, UAT, and PROD environments.
•	Participated in test case generation, code coverage, views creation, validations, and DB design.
•	Collaborated with support teams and clients to address system issues or showstoppers.
•	Conducted Integration Testing and project deployment activities using Bamboo for CI/CD.
•	Implemented role-based access control for functionalities.
•	Handled Change Requests, bug fixes, and support tickets across different applications.
•	Contributed to testing activities, defect logging, and provided fixes for the EPSD application.

Finacle Product Support                                                    					
(Under EdgeVerve subsidiary of Infosys)
(A global banking product used by various banks for maintaining Payments, Multichannel Framework, and Dashboards.) Technology: Java, IOS, Jquery, XML, Angular Js basics
Tools: Techonline, Firestone, Eclipse, Oracle Toad, Team Foundation Server, Tomcat
Roles & Responsibility:
•	Implemented bug fixes and actively resolved critical customer-reported incidents/problems within agreed SLAs.
•	Understood and swiftly delivered business enhancements.
•	Engaged in direct interaction with a Sri Lankan bank client for defect identification and fixes.

"""

    cleaned_text2 = clean_text_to_ascii(sample_text2)
    logger.info(cleaned_text2)  # Output: cleaned text without special characters, stopwords
