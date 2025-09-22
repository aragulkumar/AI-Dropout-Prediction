import React from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, Typography, Grid } from '@mui/material';
import { AttendanceChart } from '../../components/charts/AttendanceChart';
import { PerformanceChart } from '../../components/charts/PerformanceChart';
import { useStudentProfile } from '../../hooks/useStudentProfile';

export const StudentProfile: React.FC = () => {
  const { studentId } = useParams<{ studentId: string }>();
  const { student, isLoading } = useStudentProfile(studentId);

  if (isLoading || !student) return <div>Loading...</div>;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Attendance Trend
            </Typography>
            <AttendanceChart data={student.attendanceHistory} />
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Academic Performance
            </Typography>
            <PerformanceChart data={student.performanceHistory} />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};