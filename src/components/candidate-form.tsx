"use client";

import React, { useState } from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { CandidateProfileSchema, type CandidateProfileInput } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {v4 as uuidv4} from 'uuid';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { useToast } from '@/hooks/use-toast';
import {
  summarizeCandidateProfileAction,
  performMatchmakingAction,
  type Candidate,
  type Job,
  publishEventAction,
  publishQueryAction
} from '@/lib/actions';
import { Users, Sparkles, Briefcase, Loader2 } from 'lucide-react';
import { useAppContext } from '@/contexts/app-context';
import ResumeUploader from '@/components/resume-uploader';
import { useSession } from 'next-auth/react';

export default function CandidateForm() {
  const { toast } = useToast();
  const { addCandidate, jobs } = useAppContext();
  const { data: session } = useSession();
  
  // Use a persistent session ID that stays the same for the user across submissions
  const [sessionId] = useState(() => {
    const userId = session?.user?.id;
    if (userId) {
      // Check if we have a stored session ID for this user
      const storedSessionId = localStorage.getItem(`candidate_session_${userId}`);
      if (storedSessionId) {
        return storedSessionId;
      }
      // Create a new session ID and store it
      const newSessionId = `candidate_session_${userId}_${Date.now()}`;
      localStorage.setItem(`candidate_session_${userId}`, newSessionId);
      return newSessionId;
    }
    // For anonymous users, create a session-based ID
    return `anonymous_candidate_${uuidv4()}`;
  });

  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [submittedProfile, setSubmittedProfile] = useState<Candidate | null>(
    null
  );
  const [potentialMatches, setPotentialMatches] = useState<
    Awaited<ReturnType<typeof performMatchmakingAction>>
  >([]);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

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
    const summaryResult = await summarizeCandidateProfileAction({ profileText: data.experienceSummary });
    setIsLoadingSummary(false);

    let finalSummary = data.experienceSummary.substring(0, 200) + '...';
    if (summaryResult.success && summaryResult.data) {
      finalSummary = summaryResult.data;
      toast({ title: 'Profile Summary Generated', description: 'AI has summarized your experience.' });
    } else {
      toast({ title: 'Summary Error', description: summaryResult.error || 'Failed to summarize profile. Using manual summary.', variant: 'destructive' });
    }

    const user_id = session?.user?.id || `cand_${Date.now()}`;
    const user_email = session?.user?.email || ''; // Get email from session
    // const session_id = uuidv4(); // Generate a unique session ID
    const newCandidate: Candidate = { ...data, id: user_id, aiSummary: finalSummary, user_email };
    addCandidate(newCandidate);
    setSubmittedProfile(newCandidate);
    toast({ title: 'Profile Submitted', description: 'Your profile has been successfully submitted.' });

    setIsLoadingMatches(true);
    const matches = await performMatchmakingAction(newCandidate, jobs);
    setPotentialMatches(matches);
    setIsLoadingMatches(false);
    setIsSubmitted(true);
    
    // Scroll to results section
    setTimeout(() => {
      const resultsElement = document.getElementById(`profile-${newCandidate.id}`);
      if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
    
    // Publish an event after successful submission
    await publishQueryAction(data.experienceSummary, user_id, sessionId);
    // await publishEventAction("candidate_submitted", newCandidate);
  };

  const handleBackToForm = () => {
    setIsSubmitted(false);
    setSubmittedProfile(null);
    setPotentialMatches([]);
    form.reset();
  };

  const handleNewSession = () => {
    // Clear the stored session and create a new one
    const userId = session?.user?.id;
    if (userId) {
      localStorage.removeItem(`candidate_session_${userId}`);
      const newSessionId = `candidate_session_${userId}_${Date.now()}`;
      localStorage.setItem(`candidate_session_${userId}`, newSessionId);
    }
    handleBackToForm();
  };

  return (
    <div className="space-y-8">
      {!isSubmitted ? (
        <section id="submit-profile">
          <h1 className="font-headline text-3xl font-bold tracking-tight text-primary-foreground mb-6 flex items-center">
            <Users className="mr-3 h-8 w-8 text-accent" /> Candidate Profile
            Submission
          </h1>
          <Card className="shadow-xl bg-card/90 border-accent/30">
            <CardHeader>
              <CardTitle className="font-headline text-2xl">
                Create Your Profile
              </CardTitle>
              <CardDescription>
                Share your details to connect with exciting job opportunities.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-6"
                >
                  <FormField
                    control={form.control}
                    name="fullName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-lg">Full Name</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="e.g., Jane Doe"
                            {...field}
                            className="text-base"
                          />
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
                          <Input
                            placeholder="e.g., JavaScript, Management, Design"
                            {...field}
                            className="text-base font-code"
                          />
                        </FormControl>
                        <FormDescription>
                          Comma-separated list of your key skills.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="experienceSummary"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-lg">
                          Experience Summary
                        </FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Summarize your professional experience..."
                            {...field}
                            rows={6}
                            className="text-base font-code"
                          />
                        </FormControl>
                        <FormDescription>
                          Our AI will also generate a concise summary for you.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="locationPreference"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-lg">
                          Location Preference
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder="e.g., Remote, NYC, London"
                            {...field}
                            className="text-base"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="space-y-2 rounded-lg border bg-card p-4 shadow-sm">
                    <h3 className="font-medium">Upload Resume (Optional)</h3>
                    <ResumeUploader />
                    <p className="text-xs text-muted-foreground">
                      Upload your resume to supplement the information in your
                      profile.
                    </p>
                  </div>
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-accent/50 transition-all duration-300 transform hover:scale-105"
                    disabled={form.formState.isSubmitting || isLoadingSummary}
                  >
                    {form.formState.isSubmitting || isLoadingSummary ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Sparkles className="mr-2 h-4 w-4" />
                    )}
                    Submit Profile & Find Matches
                  </Button>
                </form>
              </Form>
            </CardContent>
          </Card>
        </section>
      ) : (
        <SubmissionResult
          profile={submittedProfile}
          matches={potentialMatches}
          isLoading={isLoadingMatches}
          onBack={handleBackToForm}
          sessionId={sessionId}
        />
      )}
    </div>
  );
}
interface SubmissionResultProps {
  profile: Candidate | null;
  matches: Awaited<ReturnType<typeof performMatchmakingAction>>;
  isLoading: boolean;
  onBack: () => void;
  sessionId: string;
}

function SubmissionResult({
  profile,
  matches,
  isLoading,
  onBack,
  sessionId,
}: SubmissionResultProps) {
  if (!profile) {
    return null; // Or a loading/error state
  }

  return (
    <section id={`profile-${profile.id}`} className="mt-12">
      <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
        <h2 className="font-headline text-2xl font-bold tracking-tight text-green-800 dark:text-green-200 mb-2 flex items-center">
          <Briefcase className="mr-3 h-7 w-7 text-green-600 dark:text-green-400" /> Profile Submitted Successfully!
        </h2>
        <p className="text-green-700 dark:text-green-300">
          Your profile has been processed and we've found potential job matches for you.
        </p>
      </div>
      <Card className="shadow-lg bg-card/80 border-primary/30">
        <CardHeader>
          <CardTitle>Your Submitted Profile</CardTitle>
          <CardDescription>
            Here is a summary of the information you provided.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="font-bold text-lg">Full Name</h3>
            <p>{profile.fullName}</p>
          </div>
          <div>
            <h3 className="font-bold text-lg">Skills</h3>
            <p className="font-code">{profile.skills}</p>
          </div>
          <div>
            <h3 className="font-bold text-lg">Location Preference</h3>
            <p>{profile.locationPreference}</p>
          </div>
          <div>
            <h3 className="font-bold text-lg">AI-Generated Summary</h3>
            <p className="italic text-muted-foreground">
              {profile.aiSummary}
            </p>
          </div>
        </CardContent>
        <CardFooter className="flex-col items-start gap-4">
          <h3 className="font-bold text-lg">Potential Job Matches</h3>
          {isLoading ? (
            <div className="flex items-center">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              <p>Finding the best job matches for you...</p>
            </div>
          ) : matches.length > 0 ? (
            <ul className="space-y-2">
              {matches.map(({ id, name, relevance }) => (
                <li key={id} className="p-2 rounded-md bg-accent/10">
                  <p className="font-bold">{name}</p>
                  <p>Match Score: {Math.round(relevance * 100)}%</p>
                </li>
              ))}
            </ul>
          ) : (
            <p>No job matches found at this time.</p>
          )}
          <div className="flex gap-2 mt-4">
            <Button onClick={onBack} variant="outline">
              Submit Another Profile
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
  );
}