'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';

export default function SimpleDataDashboard() {
  const [resumes, setResumes] = useState<any[]>([]);
  const [jobPostings, setJobPostings] = useState<any[]>([]);
  const [compatibilityScores, setCompatibilityScores] = useState<any[]>([]);
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

  const renderAnalytics = () => {
    // Calculate analytics from the data
    const totalResumes = resumes.length;
    const totalJobPostings = jobPostings.length;
    const totalCompatibilityScores = compatibilityScores.length;
    
    // Calculate average compatibility score
    const avgScore = compatibilityScores.length > 0
      ? Math.round(compatibilityScores.reduce((sum, score) => {
          const compatData = score.compatibility_data || score;
          return sum + (compatData.compatibility_score || 0);
        }, 0) / compatibilityScores.length)
      : 0;

    // Extract top skills from resumes
    const skillsMap = new Map<string, number>();
    resumes.forEach((resume) => {
      const resumeData = resume.response || resume.resume_data || resume;
      const skills = resumeData.skills?.technical;
      if (skills) {
        [
          ...(skills.programming_languages || []),
          ...(skills.frameworks_libraries || []),
          ...(skills.cloud_platforms || []),
          ...(skills.tools_technologies || [])
        ].forEach(skill => {
          skillsMap.set(skill, (skillsMap.get(skill) || 0) + 1);
        });
      }
    });

    const topSkills = Array.from(skillsMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([skill, count]) => ({ skill, count }));

    // Extract experience levels
    const experienceLevelsMap = new Map<string, number>();
    resumes.forEach((resume) => {
      const resumeData = resume.response || resume.resume_data || resume;
      const level = resumeData.inferred_experience_level;
      if (level) {
        experienceLevelsMap.set(level, (experienceLevelsMap.get(level) || 0) + 1);
      }
    });

    const experienceLevels = Array.from(experienceLevelsMap.entries())
      .map(([level, count]) => ({ level, count }));

    // Extract industries from job postings
    const industriesMap = new Map<string, number>();
    jobPostings.forEach((posting) => {
      const jobData = posting.response?.analyze_job_posting_response?.job_posting_data ||
                     posting.job_posting_data ||
                     posting;
      const industry = jobData.industry_type;
      if (industry) {
        industriesMap.set(industry, (industriesMap.get(industry) || 0) + 1);
      }
    });

    const industries = Array.from(industriesMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([industry, count]) => ({ industry, count }));

    return (
      <div className="space-y-6">
        <h3 className="text-xl font-semibold">Analytics Overview</h3>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Resumes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalResumes}</div>
              <p className="text-xs text-muted-foreground">Parsed and analyzed</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Job Postings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalJobPostings}</div>
              <p className="text-xs text-muted-foreground">Analyzed and structured</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compatibility Scores</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalCompatibilityScores}</div>
              <p className="text-xs text-muted-foreground">Matching analyses</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg. Compatibility</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{avgScore}%</div>
              <p className="text-xs text-muted-foreground">Average match score</p>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Skills */}
          {topSkills.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Top Skills</CardTitle>
                <CardDescription>Most frequently mentioned skills in resumes</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {topSkills.map((skill, index) => (
                  <div key={skill.skill} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-xs">#{index + 1}</Badge>
                      <span className="text-sm font-medium">{skill.skill}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${(skill.count / topSkills[0].count) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-muted-foreground">{skill.count}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Experience Levels */}
          {experienceLevels.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Experience Levels</CardTitle>
                <CardDescription>Distribution of candidate experience levels</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {experienceLevels.map((level) => (
                  <div key={level.level} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{level.level}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${(level.count / totalResumes) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-muted-foreground">{level.count}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Industries */}
          {industries.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Top Industries</CardTitle>
                <CardDescription>Most common industries in job postings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {industries.map((industry, index) => (
                  <div key={industry.industry} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" className="text-xs">#{index + 1}</Badge>
                      <span className="text-sm font-medium">{industry.industry}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">{industry.count} postings</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recent Activity</CardTitle>
              <CardDescription>Latest recruitment activities</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                ...resumes.slice(0, 3).map((r) => ({
                  type: 'resume',
                  timestamp: r.created_at,
                  description: `Resume parsed for ${(r.response || r.resume_data || r).personal_details?.full_name || 'Unknown'}`
                })),
                ...jobPostings.slice(0, 3).map((j) => ({
                  type: 'job_posting',
                  timestamp: j.created_at,
                  description: `Job posting analyzed: ${(j.response?.analyze_job_posting_response?.job_posting_data || j.job_posting_data || j).job_title || 'Unknown'}`
                })),
                ...compatibilityScores.slice(0, 3).map((c) => ({
                  type: 'compatibility',
                  timestamp: c.created_at,
                  description: `Compatibility score generated: ${(c.compatibility_data || c).compatibility_score || 0}%`
                }))
              ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
                .slice(0, 6)
                .map((activity, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="mt-1">
                    {activity.type === 'resume' && <span className="text-blue-600">👤</span>}
                    {activity.type === 'job_posting' && <span className="text-green-600">💼</span>}
                    {activity.type === 'compatibility' && <span className="text-purple-600">🎯</span>}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{activity.description}</p>
                    <p className="text-xs text-muted-foreground">{formatDate(activity.timestamp)}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  const renderResumes = () => {
    if (resumes.length === 0) {
      return (
        <Alert>
          <AlertDescription>No resumes found. Upload a resume to get started.</AlertDescription>
        </Alert>
      );
    }

    return (
      <div className="space-y-4">
        {resumes.map((resume, index) => {
          // Handle nested response structure
          const resumeData = resume.response || resume.resume_data || resume;
          const sessionInfo = resumeData.session_info || resume.session_info || {};
          
          return (
            <Card key={resume.id || index} className="w-full">
              <CardHeader>
                <CardTitle className="text-lg">
                  {resumeData.personal_details?.full_name || 'Unknown Name'}
                </CardTitle>
                <CardDescription>
                  Parsed on {formatDate(resume.created_at || new Date().toISOString())} 
                  using {sessionInfo.model_used || 'Unknown model'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {resumeData.professional_summary && (
                  <div>
                    <h4 className="font-semibold mb-2">Professional Summary</h4>
                    <p className="text-sm text-muted-foreground">
                      {resumeData.professional_summary}
                    </p>
                  </div>
                )}
                
                {resumeData.inferred_experience_level && (
                  <div className="flex gap-2">
                    <Badge variant="secondary">
                      {resumeData.inferred_experience_level}
                    </Badge>
                    {resumeData.total_years_experience && (
                      <Badge variant="outline">
                        {resumeData.total_years_experience} years exp.
                      </Badge>
                    )}
                  </div>
                )}

                {resumeData.skills?.technical && (
                  <div>
                    <h4 className="font-semibold mb-2">Technical Skills</h4>
                    <div className="flex flex-wrap gap-1">
                      {[
                        ...(resumeData.skills.technical.programming_languages || []),
                        ...(resumeData.skills.technical.frameworks_libraries || []),
                        ...(resumeData.skills.technical.cloud_platforms || [])
                      ].slice(0, 10).map((skill, skillIndex) => (
                        <Badge key={skillIndex} variant="outline" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    );
  };

  const renderJobPostings = () => {
    if (jobPostings.length === 0) {
      return (
        <Alert>
          <AlertDescription>No job postings found. Analyze a job posting to get started.</AlertDescription>
        </Alert>
      );
    }

    return (
      <div className="space-y-4">
        {jobPostings.map((posting, index) => {
          // Handle nested response structure
          const jobData = posting.response?.analyze_job_posting_response?.job_posting_data || 
                         posting.job_posting_data || 
                         posting;
          const sessionInfo = posting.response?.analyze_job_posting_response?.session_info || 
                             posting.session_info || 
                             {};
          
          return (
            <Card key={posting.id || index} className="w-full">
              <CardHeader>
                <CardTitle className="text-lg">
                  {jobData.job_title || 'Unknown Job Title'}
                </CardTitle>
                <CardDescription>
                  Analyzed on {formatDate(posting.created_at || new Date().toISOString())} 
                  using {sessionInfo.model_used || 'Unknown model'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {jobData.company?.name && (
                  <div>
                    <h4 className="font-semibold mb-2">Company</h4>
                    <p className="text-sm">{jobData.company.name}</p>
                  </div>
                )}

                {jobData.industry_type && (
                  <Badge variant="outline">{jobData.industry_type}</Badge>
                )}

                {jobData.key_responsibilities && jobData.key_responsibilities.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Key Responsibilities</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {jobData.key_responsibilities.slice(0, 3).map((resp: string, respIndex: number) => (
                        <li key={respIndex} className="flex items-start">
                          <span className="mr-2">•</span>
                          <span>{resp}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {jobData.required_skills && (
                  <div>
                    <h4 className="font-semibold mb-2">Required Skills</h4>
                    <div className="flex flex-wrap gap-1">
                      {[
                        ...(jobData.required_skills.programming_languages || []),
                        ...(jobData.required_skills.frameworks_libraries || []),
                        ...(jobData.required_skills.tools_technologies || [])
                      ].slice(0, 8).map((skill, skillIndex) => (
                        <Badge key={skillIndex} variant="outline" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    );
  };

  const renderCompatibilityScores = () => {
    if (compatibilityScores.length === 0) {
      return (
        <Alert>
          <AlertDescription>No compatibility scores found. Run a matching analysis to get started.</AlertDescription>
        </Alert>
      );
    }

    return (
      <div className="space-y-4">
        {compatibilityScores.map((score, index) => {
          const compatData = score.compatibility_data || score;
          const sessionInfo = score.session_info || {};
          
          return (
            <Card key={score.id || index} className="w-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Compatibility Analysis</CardTitle>
                  <div className="px-3 py-1 rounded-full text-white text-sm font-medium bg-blue-500">
                    {compatData.compatibility_score || 0}%
                  </div>
                </div>
                <CardDescription>
                  Generated on {formatDate(score.created_at || new Date().toISOString())} 
                  using {sessionInfo.model_used || 'Unknown model'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {compatData.summary && (
                  <div>
                    <h4 className="font-semibold mb-2">Analysis Summary</h4>
                    <p className="text-sm text-muted-foreground">
                      {compatData.summary}
                    </p>
                  </div>
                )}

                {compatData.matching_skills && compatData.matching_skills.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 text-green-700">Matching Skills</h4>
                    <div className="flex flex-wrap gap-1">
                      {compatData.matching_skills.map((skill: string, skillIndex: number) => (
                        <Badge key={skillIndex} variant="default" className="text-xs bg-green-100 text-green-800">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {compatData.missing_skills && compatData.missing_skills.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 text-red-700">Missing Skills</h4>
                    <div className="flex flex-wrap gap-1">
                      {compatData.missing_skills.map((skill: string, skillIndex: number) => (
                        <Badge key={skillIndex} variant="destructive" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Data Dashboard</h2>
        <div className="text-center py-8">Loading data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Data Dashboard</h2>
          <Button onClick={fetchData} variant="outline" size="sm">
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
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Resumes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{resumes.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Job Postings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{jobPostings.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compatibility Scores</CardTitle>
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
          {renderAnalytics()}
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