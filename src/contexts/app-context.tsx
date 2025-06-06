'use client';

import type { Job, Candidate } from '@/lib/actions';
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AppContextType {
  jobs: Job[];
  candidates: Candidate[];
  addJob: (job: Job) => void;
  addCandidate: (candidate: Candidate) => void;
  getJobById: (id: string) => Job | undefined;
  getCandidateById: (id: string) => Candidate | undefined;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);

  const addJob = (job: Job) => {
    setJobs((prevJobs) => [...prevJobs, job]);
  };

  const addCandidate = (candidate: Candidate) => {
    setCandidates((prevCandidates) => [...prevCandidates, candidate]);
  };

  const getJobById = (id: string) => jobs.find(job => job.id === id);
  const getCandidateById = (id: string) => candidates.find(candidate => candidate.id === id);


  return (
    <AppContext.Provider value={{ jobs, candidates, addJob, addCandidate, getJobById, getCandidateById }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
