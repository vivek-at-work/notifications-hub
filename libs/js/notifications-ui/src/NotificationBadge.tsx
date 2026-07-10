'use client';

import Chip from '@mui/material/Chip';

import { Button } from '@notifications-hub/design-system';

export interface NotificationBadgeProps {
  count: number;
  label?: string;
}

export function NotificationBadge({ count, label = 'Notifications' }: NotificationBadgeProps) {
  return (
    <>
      <Chip label={`${label}: ${count}`} color="primary" size="small" sx={{ mr: 1 }} />
      <Button variant="outlined" size="small">
        View
      </Button>
    </>
  );
}
