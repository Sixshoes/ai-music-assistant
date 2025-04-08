import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button Component', () => {
  it('renders button with correct text', () => {
    render(<Button onClick={() => {}}>Click me</Button>);
    expect(screen.getByTestId('button')).toHaveTextContent('Click me');
  });

  it('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByTestId('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders with primary variant by default', () => {
    render(<Button onClick={() => {}}>Click me</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--primary');
  });

  it('renders with secondary variant when specified', () => {
    render(<Button onClick={() => {}} variant="secondary">Click me</Button>);
    expect(screen.getByTestId('button')).toHaveClass('button--secondary');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button onClick={() => {}} disabled>Click me</Button>);
    expect(screen.getByTestId('button')).toBeDisabled();
  });
}); 