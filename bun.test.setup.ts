import { beforeAll } from 'bun:test';

beforeAll(() => {
  // Set up happy-dom
  global.window = new (require('happy-dom').Window)();
  global.document = window.document;
  global.navigator = window.navigator;
  global.HTMLElement = window.HTMLElement;
  global.Element = window.Element;
  global.Node = window.Node;
  
  // Mock matchMedia
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => {},
    }),
  });
});