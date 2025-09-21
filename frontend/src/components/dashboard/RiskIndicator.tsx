import React from 'react';
import { CircularProgress, Box, Typography } from '@mui/material';

interface RiskIndicatorProps {
  riskLevel: 'high' | 'medium' | 'low';
  studentCount: number;
  percentage: number;
}

export const RiskIndicator: React.FC<RiskIndicatorProps> = ({
  riskLevel,
  studentCount,
  percentage
}) => {
  const getColor = () => {
    switch (riskLevel) {
      case 'high': return '#ff4444';
      case 'medium': return '#ffa500';
      case 'low': return '#4caf50';
      default: return '#gray';
    }
  };

  return (
    <Box display="flex" alignItems="center" justifyContent="center">
      <CircularProgress
        variant="determinate"
        value={percentage}
        size={120}
        thickness={4}
        sx={{ color: getColor() }}
      />
      <Box position="absolute" display="flex" flexDirection="column" alignItems="center">
        <Typography variant="h4" component="div" color="text.secondary">
          {studentCount}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {riskLevel.toUpperCase()} RISK
        </Typography>
      </Box>
    </Box>
  );
};