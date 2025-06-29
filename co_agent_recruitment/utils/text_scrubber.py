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
    remove_stopwords: bool = False,
    lemmatize: bool = False,
    min_word_length: int = 1,
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
            nltk.data.find("tokenizers/punkt")
            nltk.data.find("corpora/stopwords")
            nltk.data.find("punkt_tab")
            nltk.data.find("corpora/wordnet")
        except LookupError:
            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)
            nltk.download("stopwords", quiet=True)
            nltk.download("wordnet", quiet=True)

        # normalize unicode characters
        text = unicodedata.normalize("NFKD", text)

        # Convert to ASCII, ignoring non-ASCII characters
        text = text.encode("ascii", "ignore").decode("ascii")

        # Remove special characters (keep letters, digits, and spaces)
        # Remove special characters but keep common punctuation that might be meaningful
        text = re.sub(r"[^\w\s\-\.\@\(\)\+\/\&\%\$\#]", " ", text)

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
            stop_words = set(stopwords.words("english"))
            tokens = [token for token in tokens if token not in stop_words]

        # Join tokens back into string
        cleaned_text = " ".join(tokens)

        # Remove extra spaces
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

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

---

### 1  Contact & Personal Details&#x20;

* **Name:** Roopal Bansal
* **E-mail:** [bansalroo06@gmail.com](mailto:bansalroo06@gmail.com)
* **Mobile:** +91 770 900 3182
* **Current Role:** Senior Software Engineer, Xoriant
* **Total Experience:** 9 years (post-2014)

---

### 2  Profile Summary&#x20;

Highly skilled Software Engineer with 9 + years in enterprise applications, business-process analysis, API design, Java & Python core-module development, micro-services with NoSQL, design patterns (Java 8) and AWS (EC2, ECS, S3, Lambda) managed via Terraform. Strong problem-solver, communicator and team lead with a record of delivering high-quality solutions.

---

### 3  Key Skills & Domain Knowledge&#x20;

* **Core Development  |  Client Interaction  |  Coordination  |  Team Player**
* **Domains:** Manufacturing, Banking/Finance, Mortgage

---

### 4  Technical Stack

| Area                          | Details                                                                                                                                              | Source |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| **Technologies & Frameworks** | Core Java 8, J2EE, Spring (Core/Data/Security/Boot/Cloud), Microservices, Hibernate, JPA, JDBC, Apache Camel, REST Web Services, Python, Splunk, AWS |        |
| **Databases**                 | MS-SQL, Oracle 10g, MongoDB, PostgreSQL (NoSQL), DynamoDB                                                                                            |        |
| **Web Servers / SSH**         | Tomcat, PuTTY                                                                                                                                        |        |
| **Version Control**           | Git (Apache), Tortoise SVN                                                                                                                           |        |
| **IDEs / Dev Tools**          | Eclipse, IntelliJ, STS, JBDS, PyCharm                                                                                                                |        |
| **Build & CI/CD**             | Maven, Bamboo, Jenkins                                                                                                                               |        |
| **Testing & Utilities**       | JMeter, HP QTP, SoapUI, Postman, Squirrel 3.6, ActiveMQ, RoboMongo, Splunk, Kibana                                                                   |        |

---

### 5  Education&#x20;

| Year | Qualification | Institution                       | Score     |
| ---- | ------------- | --------------------------------- | --------- |
| 2014 | B.E. (CSE)    | I.T.M., Gwalior – RGPV University | 8.31 CGPA |
| 2010 | 12 th (CBSE)  | Carmel Convent School             | 85.2 %    |
| 2008 | 10 th (CBSE)  | Carmel Convent School             | 85.4 %    |

---

### 6  Interests&#x20;

Fitness • Swimming • Dancing • Table Tennis • Badminton

---

## 7  Professional Experience (chronological)

### 7.1  Senior Software Engineer — **Xoriant** (Jun 2020 – Present)

**Project:** *EDIS* – Mortgage-loan provisioning & document-submission platform
**Tech:** Java 8+, Python, Spring Boot, AWS (EC2 | ECS | Lambda | S3 | Step Function | DynamoDB | Redis | CloudWatch | SQS), Docker, Kafka (basics), REST micro-services, Terraform 0.13
**Tools:** IntelliJ, PyCharm, Jenkins, Sonar, Git, Splunk, Kibana, AWS Console, Maven

**Key Contributions**

* Designed & implemented complex Spring Boot APIs and micro-services backed by NoSQL.
* Architected automated disclosure module – led from requirements to delivery.
* Built event-driven architecture to process queued events.
* Daily AWS resource management (EC2, ECS, Step Function, Lambda) and IaC via Terraform.
* Mentored team; handled task allocation & defect triage.
* Migrated Swagger (SpringFox → OAPI 1.6.11) and upgraded Spring Boot 2.4.13 → 2.6.9.
* Owned production deployments; resolved prod issues within SLA.
* Performed security scans (Snyk, Sonar, Checkmarx, Twistlock, Whitesource).
* Delivered features: Webhook notifications, e-signing, e-note registration/delivery/transfer, automated MERS eRegistry, e-Vault storage.
* Introduced Redis caching; used SLF4J logging.
* Delivered ancillary projects (MDS, UPS, Fulfillment).
* Wrote custom Swagger validations, Mockito JUnits; upgraded CMA 3.1.0 → 3.1.2.

---

### 7.2  Associate Consultant — **Capgemini** (Jun 2018 – May 2020)

#### Project A: **PSD2** (EU Payment Services Directive)

*Purpose:* Expose banking APIs to third-party providers.

* **Stack:** Spring Boot micro-services, REST, JDK 1.8, MongoDB, AWS (S3, EC2, ECS), Swagger, Mule (policies)
* **Tools:** STS, Jenkins, Sonar, Splunk, Git, Postman, RoboMongo, Bitbucket, Maven
* **Highlights:** Built micro-services, applied Mule policies; containerised on ECS; wrote Splunk reports; Mockito JUnits; handled upgrades (OB CMA 3.1.0 → 3.1.2); oversaw Jenkins deployments.

#### Project B: **AVIVA – Customer** (Insurance)

* **Stack:** Java 7, Spring, Spring Boot, Micro-services, MS-SQL, Oracle 10g, Hibernate-JPA, Apache Camel, JBoss Fuse 6.2.1
* **Tools:** JBoss Developer Studio, Jenkins, SonarQube, Splunk, Git, SoapUI, SourceTree, Wiremock
* **Highlights:** Migrated APIs Fuse 6.1 → 6.2; full Scrum participation; managed OSGi bundles (UKDT); created Wiremock stubs; resolved Sonar issues; provided live deployment support.

---

### 7.3  Senior Software Engineer — **Infosys** (Sep 2014 – May 2018)

#### Project A: **BVoC – Best View of Customer**

*Consolidates high-volume customer data from multiple sources.*

* **Tech:** Java 7, JAX-RS, Spring, MS-SQL, Hibernate-JPA, Apache Camel
* **Tools:** Eclipse, SVN, Tomcat, SQL Server 2014, SharePoint, ActiveMQ, Putty, SonarQube, Git
* **Duties:** Implemented JAX-RS modules; resolved critical ‘flipping’ issue (requirements→DB design→code); handled bug tracking & peer reviews; deployed across IT & QA; delivered exception-management module; contributed to estimations.

#### Project B: **VCD – Vehicle Control Database**

*Manages vehicle availability for testing.*

* **Tech:** Java 7, Spring, Hibernate, MS-SQL
* **Tools:** IntelliJ, Maven, SVN, Squirrel, Sonar, SharePoint
* **Duties:** Built core modules; gathered requirements; drew UML (Visio); followed TDD with JUnit; fixed bugs across DEV/UAT/PROD; created DB views & validations; coordinated integration testing & Bamboo CI/CD; implemented RBAC; managed change requests & support tickets.

#### Project C: **Finacle Product Support** (EdgeVerve)

*Global banking suite for Payments, Multichannel Framework & Dashboards.*

* **Tech:** Java, iOS, jQuery, XML, basic Angular JS
* **Tools:** TechOnline, Firestone, Eclipse, Oracle Toad, TFS, Tomcat
* **Duties:** Fixed production bugs and critical incidents within SLA; delivered business enhancements rapidly; liaised directly with Sri Lankan bank client for defect analysis & resolution.

---

### 8  Additional Tools & Utilities (hands-on)&#x20;

Maven • Bamboo • SonarQube • JIRA • JMeter • HP QTP • SoapUI • Postman • ActiveMQ • Squirrel 3.6 • Twistlock • Whitesource • Wiremock • SharePoint • WinSCP • IBM WebSphere ActiveMQ

---

**End of extracted résumé.**


"""

    cleaned_text2 = clean_text_to_ascii(sample_text2)
    logger.info(
        cleaned_text2
    )  # Output: cleaned text without special characters, stopwords
