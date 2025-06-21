'use client';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React, { useState, useEffect } from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { CandidateProfileSchema, type CandidateProfileInput } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useToast } from '@/hooks/use-toast';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { summarizeCandidateProfileAction, performMatchmakingAction, type Candidate, type Job } from '@/lib/actions';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Users, Sparkles, FileText, Search, Briefcase, Loader2 } from 'lucide-react';
import { useAppContext } from '@/contexts/app-context';
import Link from 'next/link';

export default function CandidatePage() {
  const { toast } = useToast();
  const { addCandidate, jobs } = useAppContext();

  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [aiSummary, setAiSummary] = useState<string>('');
  const [submittedProfile, setSubmittedProfile] = useState<Candidate | null>(null);
  const [potentialMatches, setPotentialMatches] = useState<Awaited<ReturnType<typeof performMatchmakingAction>>>([]);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);
  const [isLoadingProcessingDocument, setIsLoadingProcessingDocument] = useState(false); // New loading state

  const form = useForm<CandidateProfileInput>({
    resolver: zodResolver(CandidateProfileSchema),
    defaultValues: {
      fullName: '',
      skills: '',
      experienceSummary: '',
      locationPreference: '',
    },
  });

  const onSubmit: SubmitHandler<CandidateProfileInput> = async (data) => {
    setIsLoadingSummary(true);
    setAiSummary('');
    const summaryResult = await summarizeCandidateProfileAction({ profileText: data.experienceSummary });
    setIsLoadingSummary(false);

    let finalSummary = data.experienceSummary.substring(0,200) + "...";
    if (summaryResult.success && summaryResult.data) {
      finalSummary = summaryResult.data;
      toast({ title: 'Profile Summary Generated', description: 'AI has summarized your experience.' });
    } else {
      toast({ title: 'Summary Error', description: summaryResult.error || 'Failed to summarize profile. Using manual summary.', variant: 'destructive' });
    }
    
    const newCandidateId = `cand_${Date.now()}`;
    const newCandidate : Candidate = { ...data, id: newCandidateId, aiSummary: finalSummary };
    addCandidate(newCandidate);
    setSubmittedProfile(newCandidate);
    toast({ title: 'Profile Submitted', description: 'Your profile has been successfully submitted.' });

    // Call /process-document endpoint
    setIsLoadingProcessingDocument(true);
    try {
      const document_text = `Full Name: ${newCandidate.fullName}\nSkills: ${newCandidate.skills}\nExperience Summary: ${newCandidate.experienceSummary}\nLocation Preference: ${newCandidate.locationPreference}`;
      const processDocumentRequest = {
        text: document_text, // Using the concatenated string with all details
        user_id: newCandidateId,
        session_id: "123"
      };
      // Use environment variable for API URL
      const apiBaseUrl = process.env.APP_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/orchestrator`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'accept': 'application/json',
        },
        body: JSON.stringify(processDocumentRequest),
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log('Successfully processed document:', responseData);
        toast({ title: 'Document Processed', description: 'Profile processed by backend for further analysis.' });
        // You might want to do something with responseData here, e.g., store it or update state
      } else {
        const errorData = await response.json();
        console.error('Failed to process document:', errorData);
        toast({ title: 'Document Processing Error', description: errorData.detail || 'Could not process document with backend.', variant: 'destructive' });
      }
    } catch (error) {
      console.error('Error calling /process-document:', error);
      toast({ title: 'API Connection Error', description: 'Could not connect to document processing service.', variant: 'destructive' });
    }
    setIsLoadingProcessingDocument(false);

    // Perform matchmaking
    setIsLoadingMatches(true);
    const matches = await performMatchmakingAction(newCandidate, jobs);
    setPotentialMatches(matches);
    setIsLoadingMatches(false);
  };
  

  return (
    <div className="space-y-8">
      <section id="submit-profile">
        <h1 className="font-headline text-3xl font-bold tracking-tight text-primary-foreground mb-6 flex items-center">
          <Users className="mr-3 h-8 w-8 text-accent" /> Candidate Profile Submission
        </h1>
        <Card className="shadow-xl bg-card/90 border-accent/30">
          <CardHeader>
            <CardTitle className="font-headline text-2xl">Create Your Profile</CardTitle>
            <CardDescription>Share your details to connect with exciting job opportunities.</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="fullName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Full Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., Jane Doe" {...field} className="text-base" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="skills"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Skills</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., JavaScript, Project Management, Graphic Design" {...field} className="text-base font-code" />
                      </FormControl>
                      <FormDescription>Comma-separated list of your key skills.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="experienceSummary"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Experience Summary</FormLabel>
                      <FormControl>
                        <Textarea placeholder="Summarize your professional experience..." {...field} rows={6} className="text-base font-code" />
                      </FormControl>
                      <FormDescription>Our AI will also generate a concise summary for you.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="locationPreference"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-lg">Location Preference</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., Remote, New York City, London" {...field} className="text-base" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button 
                  type="submit" 
                  size="lg" 
                  className="w-full bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-accent/50 transition-all duration-300 transform hover:scale-105" 
                  disabled={form.formState.isSubmitting || isLoadingSummary || isLoadingProcessingDocument || isLoadingMatches}
                >
                  {(form.formState.isSubmitting || isLoadingSummary || isLoadingProcessingDocument || isLoadingMatches) ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                  Submit Profile & Find Matches
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </section>

      {submittedProfile && (
        <section id={`profile-${submittedProfile.id}`} className="mt-12">
           <h2 className="font-headline text-2xl font-bold tracking-tight text-primary-foreground mb-4 flex items-center">
            <Briefcase className="mr-3 h-7 w-7 text-accent" /> Your Profile & Job Matches
          </h2>
          <Card className="shadow-lg bg-card/80 border-primary/30">
            <CardHeader>
              <CardTitle className="font-headline text-xl">{submittedProfile.fullName}</CardTitle>
              <CardDescription className="font-code text-sm">Skills: {submittedProfile.skills} | Location: {submittedProfile.locationPreference}</CardDescription>
            </CardHeader>
            <CardContent>
              <h4 className="font-semibold mb-1 text-muted-foreground">AI Generated Summary:</h4>
              {isLoadingSummary && submittedProfile.id === `cand_${Date.now()}` && <div className="flex items-center"><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating summary...</div>}
              {submittedProfile.aiSummary && <p className="text-sm italic p-3 bg-muted/30 rounded-md border border-secondary">{submittedProfile.aiSummary}</p>}
              
              <h4 className="font-semibold mt-4 mb-1 text-muted-foreground">Original Experience Summary:</h4>
              <p className="text-sm whitespace-pre-line font-code">{submittedProfile.experienceSummary}</p>
            </CardContent>
            <CardFooter className="flex flex-col items-start">
              <h3 className="font-headline text-lg font-semibold mb-3 text-primary-foreground">Potential Job Matches:</h3>
              {isLoadingMatches && <div className="flex items-center w-full"><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Searching for jobs...</div>}
              {!isLoadingMatches && potentialMatches.length === 0 && <p className="text-muted-foreground">No jobs found yet, or still searching. Try having a company submit a job!</p>}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                {potentialMatches.map(match => (
                  <Card key={match.id} className="bg-background/70 hover:shadow-accent/20 transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-md text-accent">{match.name}</CardTitle>
                      <CardDescription>Relevance: {(match.relevance * 100).toFixed(0)}%</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-xs text-muted-foreground line-clamp-3">{match.details}</p>
                    </CardContent>
                    <CardFooter>
                        <Button variant="link" size="sm" className="text-accent p-0 h-auto" asChild>
                            <Link href={`/company/#job-${match.id}`}>View Full Job (mock)</Link>
                        </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </CardFooter>
          </Card>
        </section>
      )}

      {/* Removed the section that displayed "currentProfile" based on the last global candidate */}
      {/* This ensures candidates only see the profile they submitted in the current session */}

    </div>
  );
}
