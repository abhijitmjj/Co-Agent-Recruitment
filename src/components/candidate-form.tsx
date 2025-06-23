"use client";

import React, { useState } from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { CandidateProfileSchema, type CandidateProfileInput } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
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

export default function CandidateForm() {
  const { toast } = useToast();
  const { addCandidate, jobs } = useAppContext();

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

    const newCandidateId = `cand_${Date.now()}`;
    const newCandidate: Candidate = { ...data, id: newCandidateId, aiSummary: finalSummary };
    addCandidate(newCandidate);
    setSubmittedProfile(newCandidate);
    toast({ title: 'Profile Submitted', description: 'Your profile has been successfully submitted.' });

    setIsLoadingMatches(true);
    const matches = await performMatchmakingAction(newCandidate, jobs);
    setPotentialMatches(matches);
    setIsLoadingMatches(false);
    setIsSubmitted(true);
    // Publish an event after successful submission
    await publishQueryAction(finalSummary, newCandidateId, Date.now().toString());
    // await publishEventAction("candidate_submitted", newCandidate);
  };

  const handleBackToForm = () => {
    setIsSubmitted(false);
    setSubmittedProfile(null);
    setPotentialMatches([]);
    form.reset();
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
}

function SubmissionResult({
  profile,
  matches,
  isLoading,
  onBack,
}: SubmissionResultProps) {
  if (!profile) {
    return null; // Or a loading/error state
  }

  return (
    <section id={`profile-${profile.id}`} className="mt-12">
      <h2 className="font-headline text-2xl font-bold tracking-tight text-primary-foreground mb-4 flex items-center">
        <Briefcase className="mr-3 h-7 w-7 text-accent" /> Submission
        Successful!
      </h2>
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
          <Button onClick={onBack} className="mt-4">
            Submit Another
          </Button>
        </CardFooter>
      </Card>
    </section>
  );
}