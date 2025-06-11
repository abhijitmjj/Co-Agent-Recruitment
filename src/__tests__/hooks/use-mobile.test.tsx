/**
 * @jest-environment jsdom
 */

import { renderHook, act } from "@testing-library/react";
import { useIsMobile } from "@/hooks/use-mobile";

// A mock for matchMedia that allows us to control the `matches` property
// and capture the event listener to trigger it manually.
const createMatchMediaMock = () => {
  let listeners: ((event: Partial<MediaQueryListEvent>) => void)[] = [];

  const setMedia = (matches: boolean) => {
    // Define window.matchMedia with a mock implementation
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches,
        media: query,
        onchange: null,
        addListener: jest.fn(), // Deprecated
        removeListener: jest.fn(), // Deprecated
        addEventListener: (event: string, listener: () => void) => {
          if (event === "change") {
            listeners.push(listener);
          }
        },
        removeEventListener: (event: string, listener: () => void) => {
          if (event === "change") {
            listeners = listeners.filter(l => l !== listener);
          }
        },
        dispatchEvent: jest.fn(),
      })),
    });
  };

  const triggerChange = () => {
    // When triggering a change, we also need to update the `matches` property.
    const newMatches = window.innerWidth < 768;
    setMedia(newMatches);
    listeners.forEach(listener => listener({ matches: newMatches } as MediaQueryListEvent));
  };
  
  return { setMedia, triggerChange };
};

// Helper to set the window's width
const setWindowWidth = (width: number) => {
  Object.defineProperty(window, "innerWidth", {
    writable: true,
    configurable: true,
    value: width,
  });
};

describe("useIsMobile", () => {
  let matchMediaMock: ReturnType<typeof createMatchMediaMock>;

  beforeEach(() => {
    // Create a new mock for each test to ensure isolation
    matchMediaMock = createMatchMediaMock();
  });

  it("should return false when window width is for desktop", () => {
    setWindowWidth(1024);
    matchMediaMock.setMedia(false);
    
    const { result } = renderHook(() => useIsMobile());
    
    expect(result.current).toBe(false);
  });

  it("should return true when window width is for mobile", () => {
    setWindowWidth(500);
    matchMediaMock.setMedia(true);

    const { result } = renderHook(() => useIsMobile());

    expect(result.current).toBe(true);
  });

  it("should update from desktop to mobile on resize", () => {
    // Initial setup for desktop
    setWindowWidth(1024);
    matchMediaMock.setMedia(false);
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);

    // Simulate resize to mobile
    act(() => {
      setWindowWidth(500);
      matchMediaMock.triggerChange();
    });

    expect(result.current).toBe(true);
  });

  it("should update from mobile to desktop on resize", () => {
    // Initial setup for mobile
    setWindowWidth(500);
    matchMediaMock.setMedia(true);
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(true);

    // Simulate resize to desktop
    act(() => {
      setWindowWidth(1024);
      matchMediaMock.triggerChange();
    });

    expect(result.current).toBe(false);
  });
});