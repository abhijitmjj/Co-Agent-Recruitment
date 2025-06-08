'use client'; // Add this if not already present
import { Button } from '@/components/ui/button';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { ArrowRight, Bot, Briefcase, Users, Zap } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { useSession } from 'next-auth/react'; // Import useSession

export default function Home() {
  const { data: session } = useSession();
  const userRole = session?.user?.role;
  const featureRoleRestrictionEnabled = process.env.NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED === 'true';

  const canShowCompanyLink = !featureRoleRestrictionEnabled || !session || (userRole === 'enterprise');
  const canShowCandidateLink = !featureRoleRestrictionEnabled || !session || (userRole === 'candidate');

  return (
    <div className="flex flex-col items-center justify-center space-y-12">
      <section className="text-center w-full py-12 md:py-20 lg:py-28">
        <div className="container px-4 md:px-6">
          <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
            <div className="flex flex-col justify-center space-y-4">
              <div className="space-y-2">
                <h1 className="font-headline text-4xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-secondary">
                  A2A Hire: Intelligent Recruitment
                </h1>
                <p className="max-w-[600px] text-muted-foreground md:text-xl font-body">
                  AI agents collaborate via A2A to match companies and candidates perfectly, ensuring efficient, secure, and smart hiring.
                </p>
              </div>
              <div className="flex flex-col gap-3 min-[400px]:flex-row">
                {canShowCompanyLink && (
                  <Button asChild size="lg" className="group bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-accent/50 transition-all duration-300 transform hover:scale-105">
                    <Link href="/company">
                      For Companies <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </Button>
                )}
                {canShowCandidateLink && (
                  <Button asChild size="lg" variant="outline" className="group border-accent text-accent hover:bg-accent/10 hover:shadow-lg hover:shadow-accent/30 transition-all duration-300 transform hover:scale-105">
                    <Link href="/candidate">
                      For Candidates <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </Button>
                )}
              </div>
            </div>
            <Image
              src="https://placehold.co/600x400.png"
              alt="AI Recruitment"
              data-ai-hint="AI recruitment network"
              width={600}
              height={400}
              className="mx-auto aspect-video overflow-hidden rounded-xl object-cover sm:w-full lg:order-last animate-pulse-glow"
            />
          </div>
        </div>
      </section>

      <section className="w-full py-12 md:py-20 lg:py-28 bg-background">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <div className="inline-block rounded-lg bg-muted px-3 py-1 text-sm text-accent font-medium font-headline">Key Features</div>
              <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl font-headline text-primary-foreground">Revolutionizing Hiring with AI Collaboration</h2>
              <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed font-body">
                Our platform leverages distinct AI agents for companies and candidates, orchestrated by a central matchmaking intelligence to find the perfect fit.
              </p>
            </div>
          </div>
          <div className="mx-auto grid max-w-5xl items-start gap-8 sm:grid-cols-2 md:gap-12 lg:grid-cols-3 lg:gap-16 mt-12">
            <FeatureCard
              icon={<Briefcase className="h-8 w-8 text-accent" />}
              title="Company Agent"
              description="Submit job descriptions with ease. Detail job titles, responsibilities, and required skills to find top talent."
            />
            <FeatureCard
              icon={<Users className="h-8 w-8 text-accent" />}
              title="Candidate Agent"
              description="Showcase your profile. Submit skills, experience summaries, and location preferences to connect with ideal opportunities."
            />
            <FeatureCard
              icon={<Zap className="h-8 w-8 text-accent" />}
              title="AI Matchmaking"
              description="Our Orchestrator Agent uses advanced AI to compare profiles and job specs, proposing ideal matches and enhancing visibility with SEO insights."
            />
          </div>
        </div>
      </section>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <Card className="bg-card/80 hover:bg-card transition-all duration-300 ease-in-out transform hover:scale-105 shadow-lg hover:shadow-accent/20">
      <CardHeader className="flex flex-row items-center gap-4 pb-2">
        {icon}
        <CardTitle className="font-headline text-xl text-primary-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground font-body">{description}</p>
      </CardContent>
    </Card>
  );
}
