'use client';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React, { useState, useEffect, useMemo, use } from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { JobDescriptionSchema, type JobDescriptionInput } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Label } from '@/components/ui/label'; // Keep if used, but FormLabel is preferred
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useToast } from '@/hooks/use-toast';
import { getSuggestedJobTitlesAction, generateSEOKeywordsAction, performMatchmakingAction, type Candidate, type Job, type MatchResult, publishQueryAction } from '@/lib/actions';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Briefcase, Lightbulb, Search, Sparkles, UserCheck, Loader2, Eye } from 'lucide-react';
import { useAppContext } from '@/contexts/app-context';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Link from 'next/link';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogClose } from "@/components/ui/dialog";
import { ScrollArea } from '@/components/ui/scroll-area';
import { CondenseJobDataInput, condenseJobData }  from '@/ai/flows/condense-job-data'
import { useSession } from 'next-auth/react';
// Removed unused import: da from 'date-fns/locale'
import {v4 as uuidv4} from 'uuid';

export default function CompanyPage() {
  const { toast } = useToast();
  const { addJob, candidates, jobs, getCandidateById } = useAppContext();
  const { data: session } = useSession();
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [suggestedTitles, setSuggestedTitles] = useState<string[]>([]);
  const [submittedJob, setSubmittedJob] = useState<Job | null>(null);
  const [seoKeywords, setSeoKeywords] = useState<string[]>([]);
  const [isLoadingSeo, setIsLoadingSeo] = useState(false);
  const [potentialMatches, setPotentialMatches] = useState<MatchResult[]>([]);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);
  const [selectedCandidateDetail, setSelectedCandidateDetail] = useState<Candidate | null>(null);
  const [isCandidateDetailModalOpen, setIsCandidateDetailModalOpen] = useState(false);
  const [isJobSubmitted, setIsJobSubmitted] = useState(false);
  
  // Use a persistent session ID that stays the same for the user across submissions
  const [sessionId] = useState(() => {
    const userId = session?.user?.id;
    if (userId) {
      // Check if we have a stored session ID for this user
      const storedSessionId = localStorage.getItem(`company_session_${userId}`);
      if (storedSessionId) {
        return storedSessionId;
      }
      // Create a new session ID and store it
      const newSessionId = `company_session_${userId}_${Date.now()}`;
      localStorage.setItem(`company_session_${userId}`, newSessionId);
      return newSessionId;
    }
    // For anonymous users, create a session-based ID
    return `anonymous_company_${uuidv4()}`;
  });

  const form = useForm<JobDescriptionInput>({
    resolver: zodResolver(JobDescriptionSchema),
    defaultValues: {
      jobTitle: '',
      responsibilities: '',
      requiredSkills: '',
      company: '', // Default company name, can be customized
      location: '', // Default location, can be customized
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
    const newJobId = `job_${data.company}_${Date.now()}`;
    const user_id = session?.user?.id || `cand_${Date.now()}`;
    // const user_email = session?.user?.email || ''; // Get email from session - unused
    // const session_id = uuidv4(); // Generate a unique session ID
    const newJob: Job = { ...data, id: newJobId, company: data.company }; // Use the submitted company name
    addJob(newJob);
    setSubmittedJob(newJob); // Set this to display the newly submitted job's details and matches
    setIsJobSubmitted(true); // Hide the form and show results
    toast({ title: 'Job Submitted', description: 'Your job description has been successfully submitted.' });
    // Don't reset form immediately - let user see their submission first
    setSuggestedTitles([]); // Clear suggestions after submission

    // Generate SEO Keywords
    setIsLoadingSeo(true);
    const seoResult = await generateSEOKeywordsAction({
      jobTitle: data.jobTitle,
      jobDescription: data.responsibilities,
      candidateSkills: [], 
      candidateExperience: '', 
    });
    setIsLoadingSeo(false);
    if (seoResult.success && seoResult.data) {
      setSeoKeywords(seoResult.data);
    } else {
      toast({ title: 'SEO Keywords Error', description: seoResult.error || 'Failed to generate SEO keywords.', variant: 'destructive' });
    }
    let enrichedJobString = '';
    try {
      const condensedJobInput: CondenseJobDataInput = {
        jobDescription: data.responsibilities,
        jobTitle: data.jobTitle,
        companyName: data.company,
        location: data.location,
        responsibilities: data.responsibilities,
        requiredSkills: data.requiredSkills,
      };
      const enriched = await condenseJobData(condensedJobInput);
      if (enriched && typeof enriched === 'object') {
        enrichedJobString = JSON.stringify(enriched, null, 2);
      } else if (typeof enriched === 'string') {
        enrichedJobString = enriched;
      }
    } catch {
      enrichedJobString = 'GenAI enrichment failed.';
    }
    await publishQueryAction(enrichedJobString, user_id, sessionId);
    // Perform matchmaking for the new job
    setIsLoadingMatches(true);
    const matchesResult = await performMatchmakingAction(newJob, candidates);
    setPotentialMatches(matchesResult.success ? matchesResult.data || [] : []);
    setIsLoadingMatches(false);
    
    // Scroll to results section
    setTimeout(() => {
      const jobDetailsElement = document.getElementById('job-details');
      if (jobDetailsElement) {
        jobDetailsElement.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  const handleSubmitAnother = () => {
    setSubmittedJob(null);
    setPotentialMatches([]);
    setSeoKeywords([]);
    setIsJobSubmitted(false); // Show the form again
    form.reset();
    // Scroll back to the form
    const submitJobElement = document.getElementById('submit-job');
    if (submitJobElement) {
      submitJobElement.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // const handleNewSession = () => {
  //   // Clear the stored session and create a new one
  //   const userId = session?.user?.id;
  //   if (userId) {
  //     localStorage.removeItem(`company_session_${userId}`);
  //     const newSessionId = `company_session_${userId}_${Date.now()}`;
  //     localStorage.setItem(`company_session_${userId}`, newSessionId);
  //   }
  //   handleSubmitAnother();
  // };

  const currentJobs = useMemo(() => jobs.filter(job => job.company === form.getValues('company')), [jobs, form]);

  const handleViewCandidateProfile = (candidateId: string) => {
    const candidate = getCandidateById(candidateId);
    if (candidate) {
      setSelectedCandidateDetail(candidate);
      setIsCandidateDetailModalOpen(true);
    } else {
      toast({ title: 'Error', description: 'Candidate details not found.', variant: 'destructive' });
    }
  };

  return (
    <div className="space-y-8">
      {!isJobSubmitted ? (
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
                <FormField
                  control={form.control}
                  name="company"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Company Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Your Company Name" {...field} className="text-base" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="location"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Location</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., Remote, New York, London" {...field} className="text-base" />
                      </FormControl>
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
      ) : null}

      {submittedJob && (
        <section id="job-details" className="mt-12">
          <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <h2 className="font-headline text-2xl font-bold tracking-tight text-green-800 dark:text-green-200 mb-2 flex items-center">
              <UserCheck className="mr-3 h-7 w-7 text-green-600 dark:text-green-400" /> Job Posted Successfully!
            </h2>
            <p className="text-green-700 dark:text-green-300">
              Your job posting has been processed and we&apos;ve found potential candidate matches for you.
            </p>
          </div>
          <Card className="shadow-lg bg-card/80 border-primary/30">
            <CardHeader>
              <CardTitle className="font-headline text-xl">{submittedJob.jobTitle}</CardTitle>
              <CardDescription className="font-code text-sm">Required Skills: {submittedJob.requiredSkills}</CardDescription>
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
                {!isLoadingMatches && potentialMatches.length === 0 && <p className="text-muted-foreground">No candidates found yet for this job. Try submitting a candidate profile or broadening job criteria.</p>}
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
                       <Button variant="link" size="sm" className="text-accent p-0 h-auto" onClick={() => handleViewCandidateProfile(match.id)}>
                            <Eye className="mr-1 h-4 w-4" /> View Full Profile
                        </Button>
                    </CardFooter>
                    </Card>
                ))}
                </div>
                <div className="flex gap-2 mt-6 pt-4 border-t">
                  <Button onClick={handleSubmitAnother} variant="outline">
                    Submit Another Job
                  </Button>
                  <Button
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    variant="secondary"
                  >
                    Back to Top
                  </Button>
                </div>
                <div className="mt-2 text-center">
                  <p className="text-xs text-muted-foreground mb-2">
                    Session ID: {sessionId.slice(-8)}... (reused across submissions)
                  </p>
                </div>
           </CardFooter>
         </Card>
       </section>
     )}

      {currentJobs.length > 0 && !isJobSubmitted && (
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
                        async function fetchDataForJob() {
                            setIsLoadingSeo(true);
                            const seoResult = await generateSEOKeywordsAction({ jobTitle: job.jobTitle, jobDescription: job.responsibilities, candidateSkills: [], candidateExperience: '' });
                            if (seoResult.success && seoResult.data) setSeoKeywords(seoResult.data); else setSeoKeywords([]);
                            setIsLoadingSeo(false);

                            setIsLoadingMatches(true);
                            const jobMatchesResult = await performMatchmakingAction(job, candidates);
                            setPotentialMatches(jobMatchesResult.success ? jobMatchesResult.data || [] : []);
                            setIsLoadingMatches(false);
                        }
                        fetchDataForJob();
                        // Scroll to the job details section
                        const jobDetailsElement = document.getElementById('job-details');
                        if (jobDetailsElement) {
                            jobDetailsElement.scrollIntoView({ behavior: 'smooth' });
                        } else { // Fallback for older browsers or if ID isn't found immediately
                           window.scrollTo({ top: (document.getElementById('submit-job')?.offsetHeight || 0) + 100, behavior: 'smooth' });
                        }
                    }}>
                        View Details & Matches
                    </Button>
                 </CardFooter>
               </Card>
             ))}
           </div>
         </section>
      )}

      {selectedCandidateDetail && (
        <Dialog open={isCandidateDetailModalOpen} onOpenChange={setIsCandidateDetailModalOpen}>
          <DialogContent className="sm:max-w-[600px] bg-card text-card-foreground">
            <DialogHeader>
              <DialogTitle className="font-headline text-2xl text-accent">{selectedCandidateDetail.fullName}</DialogTitle>
              <DialogDescription>
                Location Preference: {selectedCandidateDetail.locationPreference}
              </DialogDescription>
            </DialogHeader>
            <ScrollArea className="max-h-[60vh] p-1 pr-4">
              <div className="space-y-4 py-4">
                <div>
                  <h4 className="font-semibold text-primary-foreground mb-1">Skills:</h4>
                  <p className="text-sm font-code bg-muted/30 p-2 rounded-md border border-secondary">{selectedCandidateDetail.skills}</p>
                </div>
                {selectedCandidateDetail.aiSummary && (
                  <div>
                    <h4 className="font-semibold text-primary-foreground mb-1">AI Generated Summary:</h4>
                    <p className="text-sm italic bg-muted/30 p-3 rounded-md border border-secondary">{selectedCandidateDetail.aiSummary}</p>
                  </div>
                )}
                <div>
                  <h4 className="font-semibold text-primary-foreground mb-1">Full Experience Summary:</h4>
                  <p className="text-sm whitespace-pre-line font-code bg-muted/30 p-3 rounded-md border border-secondary">{selectedCandidateDetail.experienceSummary}</p>
                </div>
              </div>
            </ScrollArea>
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="outline">
                  Close
                </Button>
              </DialogClose>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

