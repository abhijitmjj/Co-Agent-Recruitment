'use client';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React, { useState, useEffect, useMemo } from 'react';
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
import { 
  getSuggestedJobTitlesAction, 
  generateSEOKeywordsAction, 
  performMatchmakingAction, 
  type Candidate, 
  type Job,
  publishEventAction, 
  publishQueryAction,
  processJobWithOrchestratorAction // Ensure this is imported from @/lib/actions
} from '@/lib/actions';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Briefcase, Lightbulb, Search, Sparkles, UserCheck, Loader2, Eye } from 'lucide-react';
import { useAppContext } from '@/contexts/app-context';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Link from 'next/link';
import { useSession } from 'next-auth/react'; // Ensured import
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogClose } from "@/components/ui/dialog";
import { ScrollArea } from '@/components/ui/scroll-area';
import { v4 as uuidv4 } from 'uuid'; // Import uuid

export default function CompanyPage() {
  const { toast } = useToast();
  const { addJob, candidates, jobs, getCandidateById } = useAppContext();
  const { data: session } = useSession(); // Get session data
  
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [suggestedTitles, setSuggestedTitles] = useState<string[]>([]);
  const [submittedJob, setSubmittedJob] = useState<Job | null>(null);
  const [seoKeywords, setSeoKeywords] = useState<string[]>([]);
  const [isLoadingSeo, setIsLoadingSeo] = useState(false);
  const [potentialMatches, setPotentialMatches] = useState<Awaited<ReturnType<typeof performMatchmakingAction>>>([]);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);
  const [isProcessingOrchestrator, setIsProcessingOrchestrator] = useState(false); // Ensured state variable

  const [selectedCandidateDetail, setSelectedCandidateDetail] = useState<Candidate | null>(null);
  const [isCandidateDetailModalOpen, setIsCandidateDetailModalOpen] = useState(false);

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
    const newJobId = uuidv4(); // Generate UUID for the new job ID
    const user_id = session?.user?.email || 'anonymous_company_user';
    const session_id = session?.user?.id || Date.now().toString();

    setIsProcessingOrchestrator(true); // Set loading state for orchestrator

    // Combine job details into a single text for the orchestrator
    const jobTextForOrchestrator = `Job Title: ${data.jobTitle}\\nResponsibilities: ${data.responsibilities}\\nRequired Skills: ${data.requiredSkills}`;

    // 1. Call the action to process the job posting via the ADK orchestrator
    const orchestratorResult = await processJobWithOrchestratorAction({
      jobText: jobTextForOrchestrator,
      user_id,
      session_id
    });

    setIsProcessingOrchestrator(false); // Clear loading state for orchestrator

    if (!orchestratorResult.success) {
      toast({
        title: 'Orchestrator Processing Error',
        description: orchestratorResult.error || 'Failed to process job posting via orchestrator.',
        variant: 'destructive',
      });
      return;
    }
    
    toast({ title: 'Job Posting Processed by AI', description: 'AI has processed the job details via orchestrator.' });

    // Create the newJob object with orchestrator data
    const newJob: Job = { 
      ...data, 
      id: newJobId, // Use the generated UUID
      companyName: session?.user?.name || "Your Company", // Use session name or default
      user_id, // Included from Job type update
      session_id, // Included from Job type update
      processedDataFromOrchestrator: orchestratorResult.data // Included from Job type update
    };
    
    addJob(newJob);
    setSubmittedJob(newJob); 
    
    // 2. Publish events after successful orchestrator processing and local update
    try {
      await publishEventAction("job_description_submitted", newJob);
      const queryText = data.responsibilities || jobTextForOrchestrator; // Use responsibilities or full text for query
      await publishQueryAction(queryText, newJobId, session_id); // Use the same newJobId (UUID)
      toast({ title: 'Job Submitted & Published', description: 'Your job description has been successfully submitted and published to event stream.' });
    } catch (error) {
      console.error("Failed to publish job events:", error);
      toast({ title: 'Event Publishing Error', description: 'Failed to publish job events.', variant: 'destructive' });
    }
    
    form.reset();
    setSuggestedTitles([]);

    // Generate SEO Keywords (can run after main submission logic
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

    // Perform matchmaking for the new job
    setIsLoadingMatches(true);
    const matches = await performMatchmakingAction(newJob, candidates);
    setPotentialMatches(matches);
    setIsLoadingMatches(false);
  };
  
  const currentJobs = useMemo(() => jobs.filter(job => job.companyName === "Your Company"), [jobs]);

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
                <Button 
                  type="submit" 
                  size="lg" 
                  className="w-full bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-accent/50 transition-all duration-300 transform hover:scale-105" 
                  disabled={form.formState.isSubmitting || isLoadingSuggestions || isProcessingOrchestrator || isLoadingSeo || isLoadingMatches} // Added isProcessingOrchestrator
                >
                  {(form.formState.isSubmitting || isProcessingOrchestrator) ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />} {/* Updated loading condition */}
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
            <UserCheck className="mr-3 h-7 w-7 text-accent" /> Job Details & Candidate Matches
          </h2>
          <Card className="shadow-lg bg-card/80 border-primary/30">
            <CardHeader>
              <CardTitle className="font-headline text-xl">{submittedJob.jobTitle}</CardTitle>
              {/* Display user_id and session_id if they exist on submittedJob */}
              <CardDescription className="font-code text-sm"> 
                Company: {submittedJob.companyName} 
                {submittedJob.user_id && `| User ID: ${submittedJob.user_id}`}
                {submittedJob.session_id && ` | Session ID: ${submittedJob.session_id}`}
              </CardDescription>
              <CardDescription className="font-code text-sm">Required Skills: {submittedJob.requiredSkills}</CardDescription>
            </CardHeader>
            <CardContent>
              <h4 className="font-semibold mb-1 text-muted-foreground">Responsibilities:</h4>
              <p className="text-sm whitespace-pre-line font-code">{submittedJob.responsibilities}</p>
              
              {/* Display orchestrator processed data if available */}
              {submittedJob.processedDataFromOrchestrator && (
                <div className="mt-4 p-3 rounded-md bg-muted/30 border border-input">
                  <h5 className="font-semibold text-sm text-primary mb-1">AI Orchestrator Insights:</h5>
                  {/* @ts-ignore next-line */}
                  {submittedJob.processedDataFromOrchestrator.job_posting_result && (
                    <pre className="text-xs italic text-muted-foreground bg-black/10 p-2 rounded overflow-x-auto">
                      {/* @ts-ignore next-line */}
                      {JSON.stringify(submittedJob.processedDataFromOrchestrator.job_posting_result, null, 2)}
                    </pre>
                  )}
                  {/* @ts-ignore next-line */}
                  {submittedJob.processedDataFromOrchestrator.session_information && (
                    <details className="mt-2 text-xs"><summary className="cursor-pointer">View Session Info (from Orchestrator)</summary>
                      <pre className="text-xs italic text-muted-foreground bg-black/10 p-2 rounded overflow-x-auto mt-1">
                        {/* @ts-ignore next-line */}
                        {JSON.stringify(submittedJob.processedDataFromOrchestrator.session_information, null, 2)}
                      </pre>
                    </details>
                  )}
                  {/* Fallback if the structure is different, e.g., older mock */}
                  {/* @ts-ignore next-line */}
                  {!submittedJob.processedDataFromOrchestrator.job_posting_result && !submittedJob.processedDataFromOrchestrator.session_information && (
                     <pre className="text-xs italic text-muted-foreground bg-black/10 p-2 rounded overflow-x-auto">
                        {/* @ts-ignore next-line */}
                        {JSON.stringify(submittedJob.processedDataFromOrchestrator, null, 2)}
                     </pre>
                  )}
                </div>
              )}

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
                        async function fetchDataForJob() {
                            setIsLoadingSeo(true);
                            const seoResult = await generateSEOKeywordsAction({ jobTitle: job.jobTitle, jobDescription: job.responsibilities, candidateSkills: [], candidateExperience: '' });
                            if (seoResult.success && seoResult.data) setSeoKeywords(seoResult.data); else setSeoKeywords([]);
                            setIsLoadingSeo(false);

                            setIsLoadingMatches(true);
                            const jobMatches = await performMatchmakingAction(job, candidates);
                            setPotentialMatches(jobMatches);
                            setIsLoadingMatches(false);
                        }
                        fetchDataForJob();
                        // Scroll to the job details section
                        const jobDetailsElement = document.getElementById('job-details');
                        if (jobDetailsElement) {
                          jobDetailsElement.scrollIntoView({ behavior: 'smooth' });
                        }
                      }}>
                       <Sparkles className="mr-2 h-4 w-4" /> Refresh Matches & SEO
                    </Button>
                 </CardFooter>
               </Card>
             ))}
           </div>
         </section>
      )}

      {/* Candidate Detail Modal */}
      <Dialog open={isCandidateDetailModalOpen} onOpenChange={setIsCandidateDetailModalOpen}>
        <DialogContent className="max-w-3xl p-6 bg-card text-card-foreground">
          <DialogHeader>
            <DialogTitle className="font-headline text-2xl text-accent">{selectedCandidateDetail?.fullName || 'Candidate Details'}</DialogTitle>
            <DialogDescription className="text-muted-foreground text-sm">
              Review the details of the candidate.
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="max-h-[60vh] p-1 pr-4">
            {selectedCandidateDetail ? (
              <div className="space-y-4 py-4">
                <div>
                  <h4 className="font-semibold text-primary-foreground mb-1">Full Name:</h4>
                  <p className="text-sm">{selectedCandidateDetail.fullName}</p>
                </div>
                {selectedCandidateDetail.user_email && (
                  <div>
                    <h4 className="font-semibold text-primary-foreground mb-1">Email:</h4>
                    <p className="text-sm">{selectedCandidateDetail.user_email}</p>
                  </div>
                )}
                <div>
                  <h4 className="font-semibold text-primary-foreground mb-1">Skills:</h4>
                  <p className="text-sm font-code bg-muted/30 p-2 rounded-md border border-secondary">{selectedCandidateDetail.skills}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-primary-foreground mb-1">Location Preference:</h4>
                  <p className="text-sm">{selectedCandidateDetail.locationPreference}</p>
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
            ) : (
              <p>Loading candidate details...</p>
            )}
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
    </div>
  );
}

