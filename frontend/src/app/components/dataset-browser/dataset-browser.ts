import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, Dataset } from '../../services/api.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-dataset-browser',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dataset-browser.html',
  styleUrls: ['./dataset-browser.css']
})
export class DatasetBrowserComponent implements OnInit {
  datasets = signal<Dataset[]>([]);
  selectedFile: File | null = null;
  datasetName = '';
  uploading = false;

  constructor(private api: ApiService) { }

  ngOnInit() {
    this.loadDatasets();
  }

  loadDatasets() {
    this.api.getDatasets().subscribe((data: Dataset[]) => this.datasets.set(data));
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  upload() {
    if (!this.selectedFile || !this.datasetName) return;
    this.uploading = true;
    this.api.uploadDataset(this.selectedFile, this.datasetName, 'SEGY').subscribe({
      next: (ds: Dataset) => {
        this.datasets.update(list => [...list, ds]);
        this.uploading = false;
        this.selectedFile = null;
        this.datasetName = '';
      },
      error: () => this.uploading = false
    });
  }
}
