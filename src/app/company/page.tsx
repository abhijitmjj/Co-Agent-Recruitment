'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { JobDescriptionSchema, type JobDescriptionInput } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useToast } from '@/hooks/use-toast';
import { getSuggestedJobTitlesAction, generateSEOKeywordsAction, performMatchmakingAction, type Candidate, type Job } from '@/lib/actions';
import { Briefcase, Lightbulb, Search, Sparkles, UserCheck, Loader2 } from 'lucide-react';
import { useAppContext } from '@/contexts/app-context';
import Link from 'next/link';

export default function CompanyPage() {
  const { toast } = useToast();
  const { addJob, candidates, jobs } = useAppContext(); // Use candidates from context for matching
  
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [suggestedTitles, setSuggestedTitles] = useState<string[]>([]);
  const [submittedJob, setSubmittedJob] = useState<Job | null>(null);
  const [seoKeywords, setSeoKeywords] = useState<string[]>([]);
  const [isLoadingSeo, setIsLoadingSeo] = useState(false);
  const [potentialMatches, setPotentialMatches] = useState<Awaited<ReturnType<typeof performMatchmakingAction>>>([]);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);

  const form = useForm<JobDescriptionInput>({
    resolver: zodResolver(JobDescriptionSchema),
    defaultValues: {
      jobTitle: '',
      responsibilities: '',
      requiredSkills: '',
    },
  });

  const handleSuggestTitles = async () => {
    const jobDescriptionValue = form.getValues('responsibilities');
    if (!jobDescriptionValue || jobDescriptionValue.length < 50) {
      toast({ title: 'Error', description: 'Please provide a more detailed job description (at least 50 characters) to suggest titles.', variant: 'destructive' });
      return;
    }
    setIsLoadingSuggestions(true);
    setSuggestedTitles([]);
    const result = await getSuggestedJobTitlesAction({ jobDescription: jobDescriptionValue });
    setIsLoadingSuggestions(false);
    if (result.success && result.data) {
      setSuggestedTitles(result.data);
      toast({ title: 'Job Titles Suggested', description: 'AI has generated some title ideas for you!' });
    } else {
      toast({ title: 'Error', description: result.error || 'Failed to suggest job titles.', variant: 'destructive' });
    }
  };

  const onSubmit: SubmitHandler<JobDescriptionInput> = async (data) => {
    const newJobId = `job_${Date.now()}`;
    const newJob: Job = { ...data, id: newJobId, companyName: "Your Company" };
    addJob(newJob);
    setSubmittedJob(newJob);
    toast({ title: 'Job Submitted', description: 'Your job description has been successfully submitted.' });
    form.reset();
    setSuggestedTitles([]);

    // Generate SEO Keywords
    setIsLoadingSeo(true);
    const seoResult = await generateSEOKeywordsAction({
      jobTitle: data.jobTitle,
      jobDescription: data.responsibilities,
      candidateSkills: [], // For MVP, we pass empty. Could be enriched later.
      candidateExperience: '', // For MVP, we pass empty.
    });
    setIsLoadingSeo(false);
    if (seoResult.success && seoResult.data) {
      setSeoKeywords(seoResult.data);
    } else {
      toast({ title: 'SEO Keywords Error', description: seoResult.error || 'Failed to generate SEO keywords.', variant: 'destructive' });
    }

    // Perform matchmaking
    setIsLoadingMatches(true);
    const matches = await performMatchmakingAction(newJob, candidates);
    setPotentialMatches(matches);
    setIsLoadingMatches(false);
  };
  
  const currentJobs = useMemo(() => jobs.filter(job => job.companyName === "Your Company"), [jobs]);


  return (
    <div className="space-y-8">
      <section id="submit-job">
        <h1 className="font-headline text-3xl font-bold tracking-tight text-primary-foreground mb-6 flex items-center">
          <Briefcase className="mr-3 h-8 w-8 text-accent" /> Company Job Submission
        </h1>
        <Card className="shadow-xl bg-card/90 border-accent/30">
          <CardHeader>
            <CardTitle className="font-headline text-2xl">Post a New Job Opening</CardTitle>
            <CardDescription>Fill in the details below to attract the best talent.</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="jobTitle"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Job Title</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., Senior Software Engineer" {...field} className="text-base" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="responsibilities"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Responsibilities</FormLabel>
                      <FormControl>
                        <Textarea placeholder="Describe the key responsibilities..." {...field} rows={6} className="text-base font-code" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                { (form.getValues('responsibilities')?.length || 0) > 0 && (
                  <Button type="button" variant="outline" onClick={handleSuggestTitles} disabled={isLoadingSuggestions} className="text-accent border-accent hover:bg-accent/10">
                    {isLoadingSuggestions ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Lightbulb className="mr-2 h-4 w-4" />}
                    Suggest Job Titles (AI)
                  </Button>
                )}
                {suggestedTitles.length > 0 && (
                  <Card className="bg-background/50 border-primary/50 p-4 mt-2">
                    <CardTitle className="text-md font-headline mb-2 text-primary">AI Suggested Titles:</CardTitle>
                    <ul className="list-disc list-inside space-y-1">
                      {suggestedTitles.map((title, index) => (
                        <li key={index} className="text-sm text-foreground hover:text-accent cursor-pointer" onClick={() => form.setValue('jobTitle', title)}>
                          {title}
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}
                <FormField
                  control={form.control}
                  name="requiredSkills"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Required Skills</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., React, Node.js, Python" {...field} className="text-base font-code" />
                      </FormControl>
                      <FormDescription>Comma-separated list of skills.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button type="submit" size="lg" className="w-full bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-accent/50 transition-all duration-300 transform hover:scale-105" disabled={form.formState.isSubmitting}>
                  {form.formState.isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                  Submit Job & Find Matches
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </section>

      {submittedJob && (
        <section id="job-details" className="mt-12">
           <h2 className="font-headline text-2xl font-bold tracking-tight text-primary-foreground mb-4 flex items-center">
            <UserCheck className="mr-3 h-7 w-7 text-accent" /> Recently Submitted Job & Matches
          </h2>
          <Card className="shadow-lg bg-card/80 border-primary/30">
            <CardHeader>
              <CardTitle className="font-headline text-xl">{submittedJob.jobTitle}</CardTitle>
              <CardDescription className="font-code text-sm">Skills: {submittedJob.requiredSkills}</CardDescription>
            </CardHeader>
            <CardContent>
              <h4 className="font-semibold mb-1 text-muted-foreground">Responsibilities:</h4>
              <p className="text-sm whitespace-pre-line font-code">{submittedJob.responsibilities}</p>
              
              {isLoadingSeo && <div className="flex items-center mt-4"><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating SEO Keywords...</div>}
              {seoKeywords.length > 0 && (
                <div className="mt-6 p-4 rounded-md bg-muted/50 border border-secondary">
                  <h4 className="font-headline text-md font-semibold mb-2 text-secondary-foreground flex items-center"><Sparkles className="mr-2 h-5 w-5 text-secondary" />AI-Generated SEO Keywords:</h4>
                  <div className="flex flex-wrap gap-2">
                    {seoKeywords.map((keyword, index) => (
                      <span key={index} className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-xs font-medium shadow-sm">{keyword}</span>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
             <CardFooter className="flex flex-col items-start">
                <h3 className="font-headline text-lg font-semibold mb-3 text-primary-foreground">Potential Candidate Matches:</h3>
                {isLoadingMatches && <div className="flex items-center w-full"><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Searching for candidates...</div>}
                {!isLoadingMatches && potentialMatches.length === 0 && <p className="text-muted-foreground">No candidates found yet, or still searching. Try submitting a candidate profile!</p>}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                {potentialMatches.map(match => (
                    <Card key={match.id} className="bg-background/70 hover:shadow-accent/20 transition-shadow">
                    <CardHeader>
                        <CardTitle className="text-md text-accent">{match.name}</CardTitle>
                        <CardDescription>Relevance: { (match.relevance * 100).toFixed(0) }%</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-xs text-muted-foreground line-clamp-3">{match.details}</p>
                    </CardContent>
                    <CardFooter>
                       <Button variant="link" size="sm" className="text-accent p-0 h-auto" asChild>
                            <Link href={`/candidate/#profile-${match.id}`}>View Full Profile (mock)</Link>
                        </Button>
                    </CardFooter>
                    </Card>
                ))}
                </div>
            </CardFooter>
          </Card>
        </section>
      )}

      {currentJobs.length > 0 && !submittedJob && (
         <section id="my-jobs" className="mt-12">
           <h2 className="font-headline text-2xl font-bold tracking-tight text-primary-foreground mb-4">
             Your Posted Jobs
           </h2>
           <div className="space-y-4">
             {currentJobs.map(job => (
               <Card key={job.id} className="shadow-md bg-card/70">
                 <CardHeader>
                   <CardTitle className="font-headline text-lg">{job.jobTitle}</CardTitle>
                 </CardHeader>
                 <CardContent>
                   <p className="text-sm text-muted-foreground line-clamp-2">{job.responsibilities}</p>
                 </CardContent>
                 <CardFooter>
                    <Button variant="outline" size="sm" onClick={() => {
                        setSubmittedJob(job);
                        // Re-fetch matches and SEO for this job
                        async function fetchData() {
                            setIsLoadingSeo(true);
                            const seoResult = await generateSEOKeywordsAction({ jobTitle: job.jobTitle, jobDescription: job.responsibilities, candidateSkills: [], candidateExperience: '' });
                            if (seoResult.success) setSeoKeywords(seoResult.data || []);
                            setIsLoadingSeo(false);

                            setIsLoadingMatches(true);
                            const matches = await performMatchmakingAction(job, candidates);
                            setPotentialMatches(matches);
                            setIsLoadingMatches(false);
                        }
                        fetchData();
                        window.scrollTo({ top: document.getElementById('job-details')?.offsetTop || 0, behavior: 'smooth' });
                    }}>
                        View Details & Matches
                    </Button>
                 </CardFooter>
               </Card>
             ))}
           </div>
         </section>
      )}
    </div>
  );
}

// Ensure AppProvider wraps layout or page for context to work
// This can be done in a new app/providers.tsx file which wraps children in RootLayout
// Or directly in RootLayout for simplicity in this MVP.
// For now, I'll assume context is available.
