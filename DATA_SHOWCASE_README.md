# Data Showcase - Firebase Integration

This document describes the comprehensive data showcase functionality that retrieves and displays saved resumes, job postings, and compatibility scores from Firebase Firestore.

## Overview

The data showcase system provides a comprehensive view of all recruitment data stored in Firebase, including:
- **Resumes**: Parsed candidate resumes with structured data
- **Job Postings**: Analyzed job postings with extracted requirements
- **Compatibility Scores**: AI-generated matching analysis between resumes and job postings
- **Analytics**: Insights and trends from the collected data

## Architecture

### Backend API Endpoints

#### 1. Resume Data API (`/api/data/resumes`)
- **Collection**: `candidates`
- **Features**: 
  - Pagination support (limit/offset)
  - User filtering
  - Timestamp ordering
- **Data Structure**: Resume parsing results with session information

#### 2. Job Posting Data API (`/api/data/job-postings`)
- **Collection**: `jobPostings`
- **Features**: 
  - Pagination support
  - User filtering
  - Timestamp ordering
- **Data Structure**: Job posting analysis results with session information

#### 3. Compatibility Scores API (`/api/data/compatibility-scores`)
- **Collection**: `compatibility_scores`
- **Features**: 
  - Pagination support
  - User filtering
  - Timestamp ordering
- **Data Structure**: AI-generated compatibility analysis with matching/missing skills

### Frontend Components

#### 1. DataDashboard Component (`src/components/data-dashboard.tsx`)
Main dashboard component with tabbed interface:
- **Analytics Tab**: Overview with charts and insights
- **Resumes Tab**: Detailed resume cards with contact info, experience, skills
- **Job Postings Tab**: Job posting cards with requirements and company info
- **Compatibility Tab**: Compatibility score cards with detailed analysis

#### 2. DataAnalytics Component (`src/components/data-analytics.tsx`)
Analytics and insights component featuring:
- **Key Metrics**: Total counts and average compatibility scores
- **Top Skills**: Most frequently mentioned technical skills
- **Experience Levels**: Distribution of candidate experience levels
- **Industries**: Most common industries in job postings
- **Recent Activity**: Timeline of recent recruitment activities

### Pages

#### 1. Dedicated Data Page (`/data`)
- Standalone page for data showcase
- Accessible to both candidates and companies
- Authentication required

#### 2. Candidate Profile Page (`/candidate/profile`)
- Enhanced with data dashboard
- Shows candidate's own data and analytics

#### 3. Company Dashboard Page (`/company/dashboard`)
- Enhanced with data dashboard
- Shows company's recruitment data and analytics

## Data Structure

### Resume Data
```typescript
interface Resume {
  id: string;
  resume_data: {
    personal_details: {
      full_name: string;
      email?: string;
      phone_number?: string;
      location?: Location;
      links?: Link[];
    };
    professional_summary?: string;
    inferred_experience_level?: string;
    total_years_experience?: number;
    work_experience?: WorkExperience[];
    education?: Education[];
    skills?: Skills;
    certifications?: Certification[];
    projects?: Project[];
  };
  session_info: SessionInfo;
  created_at: string;
}
```

### Job Posting Data
```typescript
interface JobPosting {
  id: string;
  job_posting_data: {
    job_title: string;
    company?: HiringOrg;
    location: Location;
    years_of_experience?: string;
    key_responsibilities: string[];
    required_skills: KeySkills;
    required_qualifications?: Education[];
    industry_type?: string;
    salary_range?: string;
    type_of_employment?: string;
  };
  session_info: SessionInfo;
  created_at: string;
}
```

### Compatibility Score Data
```typescript
interface CompatibilityScore {
  id: string;
  compatibility_data: {
    compatibility_score: number;
    summary: string;
    matching_skills?: string[];
    missing_skills?: string[];
  };
  session_info: SessionInfo;
  created_at: string;
}
```

## Features

### 1. Real-time Data Fetching
- Fetches data from multiple Firestore collections simultaneously
- Error handling and loading states
- Refresh functionality

### 2. Rich Data Visualization
- **Resume Cards**: Contact information, work experience, skills, education
- **Job Posting Cards**: Company info, requirements, responsibilities, location
- **Compatibility Cards**: Score visualization, matching/missing skills analysis

### 3. Analytics and Insights
- **Skill Trends**: Most popular technical skills across resumes
- **Experience Distribution**: Breakdown of candidate experience levels
- **Industry Analysis**: Most common industries in job postings
- **Activity Timeline**: Recent recruitment activities

### 4. Interactive UI
- Tabbed interface for easy navigation
- Responsive design for mobile and desktop
- Loading skeletons and error states
- Badge system for categorization

### 5. Session Information
- Tracks which AI model was used for processing
- Timestamps for all operations
- Processing status and error information

## Security

### Authentication
- All endpoints require valid authentication
- Session-based access control
- Role-based filtering (candidates see their data, companies see their data)

### Data Privacy
- User-specific data filtering
- Secure Firebase Admin SDK integration
- Proper error handling without data leakage

## Usage

### For Candidates
1. Navigate to `/candidate/profile` or `/data`
2. View parsed resumes and compatibility scores
3. Analyze skill trends and experience levels
4. Track recruitment activity

### For Companies
1. Navigate to `/company/dashboard` or `/data`
2. View analyzed job postings and candidate matches
3. Review compatibility scores and insights
4. Monitor recruitment pipeline

### API Usage
```typescript
// Fetch resumes
const response = await fetch('/api/data/resumes?limit=10&offset=0');
const data = await response.json();

// Fetch job postings
const response = await fetch('/api/data/job-postings?userId=user123');
const data = await response.json();

// Fetch compatibility scores
const response = await fetch('/api/data/compatibility-scores');
const data = await response.json();
```

## Future Enhancements

1. **Advanced Filtering**: Filter by skills, experience level, industry
2. **Export Functionality**: Export data to CSV/PDF
3. **Bulk Operations**: Bulk delete or archive old data
4. **Advanced Analytics**: More detailed charts and trend analysis
5. **Real-time Updates**: WebSocket integration for live updates
6. **Search Functionality**: Full-text search across all data
7. **Data Visualization**: Charts and graphs for better insights

## Dependencies

- **Frontend**: React, Next.js, Tailwind CSS, Radix UI, Lucide React
- **Backend**: Firebase Admin SDK, Next.js API Routes
- **Database**: Firebase Firestore
- **Authentication**: NextAuth.js

## File Structure

```
src/
├── app/
│   ├── api/data/
│   │   ├── resumes/route.ts
│   │   ├── job-postings/route.ts
│   │   └── compatibility-scores/route.ts
│   ├── data/page.tsx
│   ├── candidate/profile/page.tsx
│   └── company/dashboard/page.tsx
├── components/
│   ├── data-dashboard.tsx
│   └── data-analytics.tsx
└── lib/
    ├── firebase-admin.ts
    └── firebase-client.ts
```

This comprehensive data showcase system provides a complete view of the recruitment pipeline, from initial resume parsing through job posting analysis to final compatibility scoring, all with rich analytics and insights.