'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Separator } from '@/components/ui/separator';
import DataAnalytics from '@/components/data-analytics';
import {
  User,
  Briefcase,
  Target,
  Calendar,
  MapPin,
  Mail,
  Phone,
  ExternalLink,
  Building,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  GraduationCap,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Award,
  Code,
  RefreshCw
} from 'lucide-react';

interface Resume {
  id: string;
  response?: Record<string, any>; // For nested response structure
  resume_data?: Record<string, any> | {
    personal_details: {
      full_name: string;
      email?: string;
      phone_number?: string;
      location?: {
        city?: string;
        state?: string;
        countryCode?: string;
      };
      links?: Array<{
        type: string;
        url: string;
      }>;
    };
    professional_summary?: string;
    inferred_experience_level?: string;
    total_years_experience?: number;
    work_experience?: Array<{
      job_title: string;
      company: string;
      location?: string;
      start_date: string;
      end_date?: string;
      is_current: boolean;
      responsibilities?: string[];
    }>;
    education?: Array<{
      institution: string;
      degree?: string;
      field_of_study?: string;
      graduation_date?: string;
    }>;
    skills?: {
      technical?: {
        programming_languages?: string[];
        frameworks_libraries?: string[];
        databases?: string[];
        cloud_platforms?: string[];
        tools_technologies?: string[];
      };
      soft_skills?: string[];
    };
    certifications?: Array<{
      name: string;
      issuing_organization: string;
      date_issued?: string;
    }>;
    projects?: Array<{
      name: string;
      description?: string;
      technologies_used?: string[];
      link?: string;
    }>;
  };
  session_info?: Record<string, any> | {
    operation_type: string;
    timestamp: string;
    model_used: string;
  };
  created_at: string;
}

interface JobPosting {
  id: string;
  response?: Record<string, any>;
  job_posting_data: {
    job_title: string;
    company?: {
      name?: string;
      description?: string;
      website_url?: string;
      application_email?: string;
    };
    location: {
      city?: string;
      state?: string;
      countryCode?: string;
      remote?: boolean;
    };
    years_of_experience?: string;
    key_responsibilities: string[];
    required_skills: {
      programming_languages?: string[];
      frameworks_libraries?: string[];
      databases?: string[];
      cloud_platforms?: string[];
      tools_technologies?: string[];
    };
    required_qualifications?: Array<{
      institution: string;
      degree?: string;
      field_of_study?: string;
    }>;
    industry_type?: string;
    salary_range?: string;
    type_of_employment?: string;
    date_posted?: string;
  };
  session_info: {
    operation_type: string;
    timestamp: string;
    model_used: string;
  };
  created_at: string;
}

interface CompatibilityScore {
  id: string;
  compatibility_data: {
    compatibility_score: number;
    summary: string;
    matching_skills?: string[];
    missing_skills?: string[];
  };
  session_info: {
    operation_type: string;
    timestamp: string;
    model_used: string;
  };
  created_at: string;
}

export default function DataDashboard() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [compatibilityScores, setCompatibilityScores] = useState<CompatibilityScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('analytics');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [resumesRes, jobPostingsRes, scoresRes] = await Promise.all([
        fetch('/api/data/resumes'),
        fetch('/api/data/job-postings'),
        fetch('/api/data/compatibility-scores')
      ]);

      if (!resumesRes.ok || !jobPostingsRes.ok || !scoresRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const [resumesData, jobPostingsData, scoresData] = await Promise.all([
        resumesRes.json(),
        jobPostingsRes.json(),
        scoresRes.json()
      ]);

      setResumes(resumesData.resumes || []);
      setJobPostings(jobPostingsData.jobPostings || []);
      setCompatibilityScores(scoresData.compatibilityScores || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const renderResumes = () => {
    // Filter resumes to only show those with valid data structure
    // Handle both direct structure and nested response structure
    const validResumes = resumes.filter(resume => {
      const resumeData = resume.response || resume.resume_data || resume;
      return resumeData &&
             (resumeData as Record<string, any>).personal_details &&
             (resumeData as Record<string, any>).personal_details.full_name;
    }).map(resume => {
      // Normalize the data structure
      const resumeData = resume.response || resume.resume_data || resume;
      return {
        ...resume,
        resume_data: resumeData as Record<string, any>,
        session_info: (resumeData as Record<string, any>).session_info || resume.session_info || {}
      };
    });

    return (
      <div className="space-y-4">
        {resumes.length === 0 ? (
          <Alert>
            <AlertDescription>No resumes found. Upload a resume to get started.</AlertDescription>
          </Alert>
        ) : validResumes.length === 0 ? (
          <Alert>
            <AlertDescription>
              Found {resumes.length} resume(s) but they have invalid data structure.
              Please check the console for details.
            </AlertDescription>
          </Alert>
        ) : (
          validResumes.map((resume) => (
          <Card key={resume.id} className="w-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <User className="h-5 w-5" />
                  <CardTitle className="text-lg">
                    {(resume.resume_data as Record<string, any>)?.personal_details?.full_name || 'Unknown Name'}
                  </CardTitle>
                </div>
                <div className="flex items-center space-x-2">
                  {(resume.resume_data as Record<string, any>).inferred_experience_level && (
                    <Badge variant="secondary">
                      {(resume.resume_data as Record<string, any>).inferred_experience_level}
                    </Badge>
                  )}
                  {(resume.resume_data as Record<string, any>).total_years_experience && (
                    <Badge variant="outline">
                      {(resume.resume_data as Record<string, any>).total_years_experience} years exp.
                    </Badge>
                  )}
                </div>
              </div>
              <CardDescription>
                Parsed on {formatDate(resume.created_at)} using {(resume.session_info as Record<string, any>)?.model_used || 'Unknown model'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Contact Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(resume.resume_data as Record<string, any>).personal_details?.email && (
                  <div className="flex items-center space-x-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{(resume.resume_data as Record<string, any>).personal_details.email}</span>
                  </div>
                )}
                {(resume.resume_data as Record<string, any>).personal_details?.phone_number && (
                  <div className="flex items-center space-x-2">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{(resume.resume_data as Record<string, any>).personal_details.phone_number}</span>
                  </div>
                )}
                {(resume.resume_data as Record<string, any>).personal_details?.location && (
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      {[
                        (resume.resume_data as Record<string, any>).personal_details.location.city,
                        (resume.resume_data as Record<string, any>).personal_details.location.state,
                        (resume.resume_data as Record<string, any>).personal_details.location.countryCode
                      ].filter(Boolean).join(', ')}
                    </span>
                  </div>
                )}
              </div>

              {/* Professional Summary */}
              {(resume.resume_data as Record<string, any>).professional_summary && (
                <div>
                  <h4 className="font-semibold mb-2">Professional Summary</h4>
                  <p className="text-sm text-muted-foreground">
                    {(resume.resume_data as Record<string, any>).professional_summary}
                  </p>
                </div>
              )}

              {/* Work Experience */}
              {(resume.resume_data as Record<string, any>).work_experience && (resume.resume_data as Record<string, any>).work_experience.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Briefcase className="h-4 w-4 mr-2" />
                    Work Experience
                  </h4>
                  <div className="space-y-2">
                    {(resume.resume_data as Record<string, any>).work_experience.slice(0, 3).map((exp: Record<string, any>, index: number) => (
                      <div key={index} className="border-l-2 border-muted pl-4">
                        <div className="flex items-center justify-between">
                          <h5 className="font-medium">{exp.job_title}</h5>
                          {exp.is_current && <Badge variant="default" className="text-xs">Current</Badge>}
                        </div>
                        <p className="text-sm text-muted-foreground">{exp.company}</p>
                        <p className="text-xs text-muted-foreground">
                          {exp.start_date} - {exp.end_date || 'Present'}
                        </p>
                      </div>
                    ))}
                    {(resume.resume_data as Record<string, any>).work_experience.length > 3 && (
                      <p className="text-xs text-muted-foreground">
                        +{(resume.resume_data as Record<string, any>).work_experience.length - 3} more positions
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Skills */}
              {(resume.resume_data as Record<string, any>).skills?.technical && (
                <div>
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Code className="h-4 w-4 mr-2" />
                    Technical Skills
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {[
                      ...((resume.resume_data as Record<string, any>).skills.technical.programming_languages || []),
                      ...((resume.resume_data as Record<string, any>).skills.technical.frameworks_libraries || []),
                      ...((resume.resume_data as Record<string, any>).skills.technical.databases || []),
                      ...((resume.resume_data as Record<string, any>).skills.technical.cloud_platforms || []),
                      ...((resume.resume_data as Record<string, any>).skills.technical.tools_technologies || [])
                    ].slice(0, 10).map((skill, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Links */}
              {(resume.resume_data as Record<string, any>).personal_details?.links && (resume.resume_data as Record<string, any>).personal_details.links.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {(resume.resume_data as Record<string, any>).personal_details.links.map((link: Record<string, any>, index: number) => (
                    <a
                      key={index}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800"
                    >
                      <ExternalLink className="h-3 w-3" />
                      <span>{link.type}</span>
                    </a>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
          ))
        )}
      </div>
    );
  };

  const renderJobPostings = () => {
    // Filter and normalize job postings data structure
    const validJobPostings = jobPostings.filter(posting => {
      const jobData = posting.response?.analyze_job_posting_response?.job_posting_data ||
                     posting.job_posting_data ||
                     posting;
      return jobData && jobData.job_title;
    }).map(posting => {
      // Normalize the data structure
      const jobData = posting.response?.analyze_job_posting_response?.job_posting_data ||
                     posting.job_posting_data ||
                     posting;
      const sessionInfo = posting.response?.analyze_job_posting_response?.session_info ||
                         posting.session_info ||
                         {};
      return {
        ...posting,
        job_posting_data: jobData,
        session_info: sessionInfo
      };
    });

    return (
      <div className="space-y-4">
        {jobPostings.length === 0 ? (
          <Alert>
            <AlertDescription>No job postings found. Analyze a job posting to get started.</AlertDescription>
          </Alert>
        ) : validJobPostings.length === 0 ? (
          <Alert>
            <AlertDescription>
              Found {jobPostings.length} job posting(s) but they have invalid data structure.
            </AlertDescription>
          </Alert>
        ) : (
          validJobPostings.map((posting) => (
          <Card key={posting.id} className="w-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Briefcase className="h-5 w-5" />
                  <CardTitle className="text-lg">
                    {posting.job_posting_data.job_title}
                  </CardTitle>
                </div>
                <div className="flex items-center space-x-2">
                  {posting.job_posting_data.type_of_employment && (
                    <Badge variant="secondary">
                      {posting.job_posting_data.type_of_employment}
                    </Badge>
                  )}
                  {posting.job_posting_data.location.remote && (
                    <Badge variant="outline">Remote</Badge>
                  )}
                </div>
              </div>
              <CardDescription>
                Analyzed on {formatDate(posting.created_at)} using {posting.session_info?.model_used || 'Unknown model'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Company Information */}
              {posting.job_posting_data.company && (
                <div className="flex items-center space-x-2">
                  <Building className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">{posting.job_posting_data.company.name}</span>
                  {posting.job_posting_data.company.website_url && (
                    <a
                      href={posting.job_posting_data.company.website_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              )}

              {/* Location and Experience */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    {[
                      posting.job_posting_data.location.city,
                      posting.job_posting_data.location.state,
                      posting.job_posting_data.location.countryCode
                    ].filter(Boolean).join(', ')}
                  </span>
                </div>
                {posting.job_posting_data.years_of_experience && (
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{posting.job_posting_data.years_of_experience} experience</span>
                  </div>
                )}
              </div>

              {/* Industry and Salary */}
              <div className="flex flex-wrap gap-2">
                {posting.job_posting_data.industry_type && (
                  <Badge variant="outline">{posting.job_posting_data.industry_type}</Badge>
                )}
                {posting.job_posting_data.salary_range && (
                  <Badge variant="outline">{posting.job_posting_data.salary_range}</Badge>
                )}
              </div>

              {/* Key Responsibilities */}
              {posting.job_posting_data.key_responsibilities && posting.job_posting_data.key_responsibilities.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Key Responsibilities</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {posting.job_posting_data.key_responsibilities.slice(0, 5).map((resp: string, index: number) => (
                      <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>{resp}</span>
                      </li>
                    ))}
                    {posting.job_posting_data.key_responsibilities.length > 5 && (
                      <li className="text-xs">+{posting.job_posting_data.key_responsibilities.length - 5} more responsibilities</li>
                    )}
                  </ul>
                </div>
              )}

              {/* Required Skills */}
              {posting.job_posting_data.required_skills && (
                <div>
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Code className="h-4 w-4 mr-2" />
                    Required Skills
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {[
                      ...(posting.job_posting_data.required_skills.programming_languages || []),
                      ...(posting.job_posting_data.required_skills.frameworks_libraries || []),
                      ...(posting.job_posting_data.required_skills.databases || []),
                      ...(posting.job_posting_data.required_skills.cloud_platforms || []),
                      ...(posting.job_posting_data.required_skills.tools_technologies || [])
                    ].slice(0, 10).map((skill, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
          ))
        )}
      </div>
    );
  };

  const renderCompatibilityScores = () => (
    <div className="space-y-4">
      {compatibilityScores.length === 0 ? (
        <Alert>
          <AlertDescription>No compatibility scores found. Run a matching analysis to get started.</AlertDescription>
        </Alert>
      ) : (
        compatibilityScores.map((score) => (
          <Card key={score.id} className="w-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Target className="h-5 w-5" />
                  <CardTitle className="text-lg">Compatibility Analysis</CardTitle>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`px-3 py-1 rounded-full text-white text-sm font-medium ${getScoreColor(score.compatibility_data.compatibility_score)}`}>
                    {score.compatibility_data.compatibility_score}%
                  </div>
                </div>
              </div>
              <CardDescription>
                Generated on {formatDate(score.created_at)} using {score.session_info?.model_used || 'Unknown model'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Summary */}
              <div>
                <h4 className="font-semibold mb-2">Analysis Summary</h4>
                <p className="text-sm text-muted-foreground">
                  {score.compatibility_data.summary}
                </p>
              </div>

              {/* Matching Skills */}
              {score.compatibility_data.matching_skills && score.compatibility_data.matching_skills.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 text-green-700">Matching Skills</h4>
                  <div className="flex flex-wrap gap-1">
                    {score.compatibility_data.matching_skills.map((skill, index) => (
                      <Badge key={index} variant="default" className="text-xs bg-green-100 text-green-800">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Skills */}
              {score.compatibility_data.missing_skills && score.compatibility_data.missing_skills.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 text-red-700">Missing Skills</h4>
                  <div className="flex flex-wrap gap-1">
                    {score.compatibility_data.missing_skills.map((skill, index) => (
                      <Badge key={index} variant="destructive" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Data Dashboard</h2>
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Data Dashboard</h2>
          <Button onClick={fetchData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
        <Alert>
          <AlertDescription>Error loading data: {error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Data Dashboard</h2>
        <Button onClick={fetchData} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Resumes</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{resumes.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Job Postings</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{jobPostings.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compatibility Scores</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{compatibilityScores.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Data Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="resumes">Resumes ({resumes.length})</TabsTrigger>
          <TabsTrigger value="job-postings">Job Postings ({jobPostings.length})</TabsTrigger>
          <TabsTrigger value="compatibility">Compatibility ({compatibilityScores.length})</TabsTrigger>
        </TabsList>
        
        <TabsContent value="analytics" className="mt-6">
          <DataAnalytics />
        </TabsContent>
        
        <TabsContent value="resumes" className="mt-6">
          <ScrollArea className="h-[600px]">
            {renderResumes()}
          </ScrollArea>
        </TabsContent>
        
        <TabsContent value="job-postings" className="mt-6">
          <ScrollArea className="h-[600px]">
            {renderJobPostings()}
          </ScrollArea>
        </TabsContent>
        
        <TabsContent value="compatibility" className="mt-6">
          <ScrollArea className="h-[600px]">
            {renderCompatibilityScores()}
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}