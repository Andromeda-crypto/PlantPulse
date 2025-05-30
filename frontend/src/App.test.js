import { render, screen } from '@testing-library/react';
import App from './App';

test('renders input fields and zoom button', () => {
  render(<App />);

  const startInput = screen.getByPlaceholderText(/start hour/i);
  const endInput = screen.getByPlaceholderText(/end hour/i);
  const zoomButton = screen.getByRole('button', { name: /zoom/i });

  expect(startInput).toBeInTheDocument();
  expect(endInput).toBeInTheDocument();
  expect(zoomButton).toBeInTheDocument();
});


