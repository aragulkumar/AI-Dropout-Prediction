import React from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import { RiskIndicator } from '../../components/dashboard/RiskIndicator';
import { StudentList } from '../../components/dashboard/StudentList';
import { useStudentData } from '../../hooks/useStudentData';

export const TeacherDashboard: React.FC = () => {
  const { students, riskSummary, isLoading } = useStudentData();

  if (isLoading) return <div>Loading...</div>;

  const calculatePercentage = (count: number, total: number) => {
    if (!total) {
      return 0;
    }
    return (count / total) * 100;
  };

  const riskCategories: {
    level: 'high' | 'medium' | 'low';
    count: number;
  }[] = [
    { level: 'high', count: riskSummary.highRisk },
    { level: 'medium', count: riskSummary.mediumRisk },
    { level: 'low', count: riskSummary.lowRisk },
  ];

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Student Risk Overview
        </Typography>
      </Grid>

      {riskCategories.map(({ level, count }) => (
        <Grid item xs={4} key={level}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <RiskIndicator
              riskLevel={level}
              studentCount={count}
              percentage={calculatePercentage(count, riskSummary.total)}
            />
          </Paper>
        </Grid>
      ))}

      <Grid item xs={12}>
        <Paper elevation={3} sx={{ p: 3 }}>
          <StudentList students={students} />
        </Paper>
      </Grid>
    </Grid>
  );
};