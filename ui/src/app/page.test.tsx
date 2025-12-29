import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Home from './page';

describe('Home Page', () => {
  it('renders the page title', () => {
    render(<Home />);
    expect(screen.getByText('Minecraft Server Dashboard')).toBeInTheDocument();
  });

  it('renders frontend status', () => {
    render(<Home />);
    expect(screen.getByText('Frontend Status')).toBeInTheDocument();
  });

  it('renders backend API status section', () => {
    render(<Home />);
    expect(screen.getByText('Backend API Status')).toBeInTheDocument();
  });

  it('renders development environment section', () => {
    render(<Home />);
    expect(screen.getByText('Development Environment')).toBeInTheDocument();
  });
});
