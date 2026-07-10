import type { Meta, StoryObj } from '@storybook/react';

import { Button } from '@notifications-hub/design-system';

const meta: Meta<typeof Button> = {
  title: 'Design System/Button',
  component: Button,
  args: {
    children: 'Click me',
    variant: 'contained',
  },
};

export default meta;

type Story = StoryObj<typeof Button>;

export const Primary: Story = {};

export const Outlined: Story = {
  args: {
    variant: 'outlined',
  },
};
