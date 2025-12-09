import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, Dataset, Job, JobStatus } from '../../services/api.service';
import { Icons } from '../../shared/icons';

@Component({
    selector: 'app-results',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './results.component.html',
    styleUrls: ['./results.component.css']
})
export class ResultsComponent implements OnInit {
    icons = Icons;
    datasets: Dataset[] = [];
    jobs: Job[] = [];
    selectedDatasetId: number | null = null;
    selectedJobId: string | null = null;
    loading = true;

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.loadData();
    }

    loadData() {
        this.loading = true;

        this.api.getDatasets().subscribe({
            next: (datasets) => {
                this.datasets = datasets;
                this.loading = false;
            },
            error: () => {
                this.datasets = [];
                this.loading = false;
            }
        });

        this.api.getJobs().subscribe({
            next: (jobs) => {
                this.jobs = jobs.filter(j => j.status === JobStatus.COMPLETED);
            },
            error: () => {
                this.jobs = [];
            }
        });
    }

    getJobsForDataset(): Job[] {
        if (!this.selectedDatasetId) return [];
        return this.jobs.filter(j => j.dataset_id === this.selectedDatasetId);
    }

    canVisualize(): boolean {
        return this.selectedJobId !== null;
    }
}
