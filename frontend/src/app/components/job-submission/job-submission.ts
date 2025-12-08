import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, Dataset, JobCreate } from '../../services/api.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-job-submission',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="submission-container">
        <h2>Submit Processing Job</h2>
        
        <div class="form-group">
            <label>Select Dataset:</label>
            <select [(ngModel)]="selectedDatasetId">
                <option *ngFor="let ds of datasets()" [value]="ds.id">{{ ds.name }}</option>
            </select>
        </div>

        <div class="form-group">
            <label>Algorithm:</label>
            <select [(ngModel)]="algorithm">
                <option value="bandpass">Bandpass Filter</option>
                <option value="decon">Deconvolution</option>
                <option value="unet">U-Net Reconstruction</option>
            </select>
        </div>

        <div class="form-group">
            <label>Parameters (JSON):</label>
            <textarea [(ngModel)]="paramsJson" rows="5"></textarea>
        </div>

        <button (click)="submit()" [disabled]="!selectedDatasetId">Submit Job</button>
    </div>
  `,
  styles: [`
    .submission-container { padding: 20px; }
    .form-group { margin-bottom: 15px; }
    label { display: block; margin-bottom: 5px; font-weight: bold; }
    textarea { width: 100%; font-family: monospace; }
  `]
})
export class JobSubmissionComponent implements OnInit {
  datasets = signal<Dataset[]>([]);
  selectedDatasetId: number | null = null;
  algorithm = 'bandpass';
  paramsJson = '{\n  "freq_low": 10,\n  "freq_high": 60\n}';

  constructor(private api: ApiService, private router: Router) { }

  ngOnInit() {
    this.api.getDatasets().subscribe((data: Dataset[]) => this.datasets.set(data));
  }

  submit() {
    if (!this.selectedDatasetId) return;
    try {
      const params = JSON.parse(this.paramsJson);
      const jobCreate: JobCreate = {
        dataset_id: this.selectedDatasetId,
        algorithm: this.algorithm,
        params: params
      };
      this.api.createJob(jobCreate).subscribe(() => {
        this.router.navigate(['/jobs']);
      });
    } catch (e) {
      alert('Invalid JSON parameters');
    }
  }
}

