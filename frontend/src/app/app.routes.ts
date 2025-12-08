import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { JobSubmissionComponent } from './pages/job-submission/job-submission.component';
import { VisualizationComponent } from './pages/visualization/visualization.component';
import { DatasetsComponent } from './pages/datasets/datasets.component';
import { SettingsComponent } from './pages/settings/settings.component';
import { ModelsComponent } from './pages/models/models.component';
import { ResultsComponent } from './pages/results/results.component';
import { SystemComponent } from './pages/system/system.component';
import { DocsComponent } from './pages/docs/docs.component';

export const routes: Routes = [
    { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
    { path: 'dashboard', component: DashboardComponent },
    { path: 'datasets', component: DatasetsComponent },
    { path: 'jobs', component: JobSubmissionComponent },
    { path: 'models', component: ModelsComponent },
    { path: 'results', component: ResultsComponent },
    { path: 'system', component: SystemComponent },
    { path: 'docs', component: DocsComponent },
    { path: 'visualize', component: VisualizationComponent },
    { path: 'settings', component: SettingsComponent },
    { path: '**', redirectTo: '/dashboard' }
];
