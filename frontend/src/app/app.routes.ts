import { Routes } from '@angular/router';
import { DatasetBrowserComponent } from './components/dataset-browser/dataset-browser';
import { JobSubmissionComponent } from './components/job-submission/job-submission';
import { JobStatusComponent } from './components/job-status/job-status';
import { SeismicViewerComponent } from './components/seismic-viewer/seismic-viewer';

export const routes: Routes = [
    { path: '', redirectTo: 'datasets', pathMatch: 'full' },
    { path: 'datasets', component: DatasetBrowserComponent, title: 'Datasets - Promethium' },
    { path: 'jobs/submit', component: JobSubmissionComponent, title: 'Submit Job - Promethium' },
    { path: 'jobs', component: JobStatusComponent, title: 'Jobs - Promethium' },
    { path: 'visualize', component: SeismicViewerComponent, title: 'Visualize - Promethium' },
    { path: '**', redirectTo: 'datasets' }
];
