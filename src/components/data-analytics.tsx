'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  TrendingUp, 
  Users, 
  Briefcase, 
  Target, 
  Award,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';

interface AnalyticsData {
  totalResumes: number;
  totalJobPostings: number;
  totalCompatibilityScores: number;
  averageCompatibilityScore: number;
  topSkills: Array<{ skill: string; count: number }>;
  experienceLevels: Array<{ level: string; count: number }>;
  industries: Array<{ industry: string; count: number }>;
  recentActivity: Array<{
    type: string;
    timestamp: string;
    description: string;
  }>;
}

export default function DataAnalytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
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

      // Process analytics
      const resumes = resumesData.resumes || [];
      const jobPostings = jobPostingsData.jobPostings || [];
      const compatibilityScores = scoresData.compatibilityScores || [];

      // Calculate average compatibility score
      const avgScore = compatibilityScores.length > 0 
        ? compatibilityScores.reduce((sum: number, score: any) => 
            sum + (score.compatibility_data?.compatibility_score || 0), 0) / compatibilityScores.length
        : 0;

      // Extract top skills from resumes
      const skillsMap = new Map<string, number>();
      resumes.forEach((resume: any) => {
        const skills = resume.resume_data?.skills?.technical;
        if (skills) {
          [
            ...(skills.programming_languages || []),
            ...(skills.frameworks_libraries || []),
            ...(skills.databases || []),
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
      resumes.forEach((resume: any) => {
        const level = resume.resume_data?.inferred_experience_level;
        if (level) {
          experienceLevelsMap.set(level, (experienceLevelsMap.get(level) || 0) + 1);
        }
      });

      const experienceLevels = Array.from(experienceLevelsMap.entries())
        .map(([level, count]) => ({ level, count }));

      // Extract industries from job postings
      const industriesMap = new Map<string, number>();
      jobPostings.forEach((posting: any) => {
        const industry = posting.job_posting_data?.industry_type;
        if (industry) {
          industriesMap.set(industry, (industriesMap.get(industry) || 0) + 1);
        }
      });

      const industries = Array.from(industriesMap.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([industry, count]) => ({ industry, count }));

      // Recent activity
      const recentActivity = [
        ...resumes.map((r: any) => ({
          type: 'resume',
          timestamp: r.created_at,
          description: `Resume parsed for ${r.resume_data?.personal_details?.full_name || 'Unknown'}`
        })),
        ...jobPostings.map((j: any) => ({
          type: 'job_posting',
          timestamp: j.created_at,
          description: `Job posting analyzed: ${j.job_posting_data?.job_title || 'Unknown'}`
        })),
        ...compatibilityScores.map((c: any) => ({
          type: 'compatibility',
          timestamp: c.created_at,
          description: `Compatibility score generated: ${c.compatibility_data?.compatibility_score || 0}%`
        }))
      ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, 10);

      setAnalytics({
        totalResumes: resumes.length,
        totalJobPostings: jobPostings.length,
        totalCompatibilityScores: compatibilityScores.length,
        averageCompatibilityScore: Math.round(avgScore),
        topSkills,
        experienceLevels,
        industries,
        recentActivity
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'resume': return <Users className="h-4 w-4" />;
      case 'job_posting': return <Briefcase className="h-4 w-4" />;
      case 'compatibility': return <Target className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'resume': return 'text-blue-600';
      case 'job_posting': return 'text-green-600';
      case 'compatibility': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Analytics Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert>
        <AlertDescription>Error loading analytics: {error}</AlertDescription>
      </Alert>
    );
  }

  if (!analytics) {
    return null;
  }

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold flex items-center">
        <BarChart3 className="h-5 w-5 mr-2" />
        Analytics Overview
      </h3>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Resumes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.totalResumes}</div>
            <p className="text-xs text-muted-foreground">Parsed and analyzed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Job Postings</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.totalJobPostings}</div>
            <p className="text-xs text-muted-foreground">Analyzed and structured</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compatibility Scores</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.totalCompatibilityScores}</div>
            <p className="text-xs text-muted-foreground">Matching analyses</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Compatibility</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.averageCompatibilityScore}%</div>
            <p className="text-xs text-muted-foreground">Average match score</p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Skills */}
        {analytics.topSkills.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Top Skills
              </CardTitle>
              <CardDescription>Most frequently mentioned skills in resumes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {analytics.topSkills.map((skill, index) => (
                <div key={skill.skill} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline" className="text-xs">#{index + 1}</Badge>
                    <span className="text-sm font-medium">{skill.skill}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Progress 
                      value={(skill.count / analytics.topSkills[0].count) * 100} 
                      className="w-20 h-2" 
                    />
                    <span className="text-xs text-muted-foreground">{skill.count}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Experience Levels */}
        {analytics.experienceLevels.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <PieChart className="h-5 w-5 mr-2" />
                Experience Levels
              </CardTitle>
              <CardDescription>Distribution of candidate experience levels</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {analytics.experienceLevels.map((level) => (
                <div key={level.level} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{level.level}</span>
                  <div className="flex items-center space-x-2">
                    <Progress 
                      value={(level.count / analytics.totalResumes) * 100} 
                      className="w-20 h-2" 
                    />
                    <span className="text-xs text-muted-foreground">{level.count}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Industries */}
        {analytics.industries.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Top Industries</CardTitle>
              <CardDescription>Most common industries in job postings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {analytics.industries.map((industry, index) => (
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
            <CardTitle className="text-lg flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              Recent Activity
            </CardTitle>
            <CardDescription>Latest recruitment activities</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {analytics.recentActivity.map((activity, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className={`mt-1 ${getActivityColor(activity.type)}`}>
                  {getActivityIcon(activity.type)}
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
}