import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, Dataset } from '../../services/api.service';
import { Icons } from '../../shared/icons';

@Component({
    selector: 'app-datasets',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './datasets.component.html',
    styleUrls: ['./datasets.component.css']
})
export class DatasetsComponent implements OnInit {
    icons = Icons;
    datasets: Dataset[] = [];
    loading = true;
    showUploadModal = false;
    submitting = false;

    uploadName = '';
    uploadFormat = 'segy';
    selectedFile: File | null = null;
    error: string | null = null;

    // Filter states
    searchTerm = '';

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.refreshDatasets();
    }

    refreshDatasets() {
        this.loading = true;
        this.error = null;
        this.api.getDatasets().subscribe({
            next: (data) => {
                this.datasets = data;
                this.loading = false;
            },
            error: (err) => {
                console.error('Failed to load datasets', err);
                this.error = 'Failed to load datasets';
                this.loading = false;
            }
        });
    }

    get filteredDatasets(): Dataset[] {
        if (!this.searchTerm) return this.datasets;
        return this.datasets.filter(d =>
            d.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
            d.format.toLowerCase().includes(this.searchTerm.toLowerCase())
        );
    }

    viewDataset(dataset: Dataset) {
        console.log('View dataset:', dataset);
    }

    deleteDataset(id: number) {
        if (confirm('Are you sure you want to delete this dataset? This action cannot be undone.')) {
            this.api.deleteDataset(id).subscribe({
                next: () => {
                    this.datasets = this.datasets.filter(d => d.id !== id);
                },
                error: (err) => {
                    alert('Failed to delete dataset: ' + err.message);
                }
            });
        }
    }

    onFileSelect(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            this.selectedFile = input.files[0];
        }
    }

    onFileDrop(event: DragEvent) {
        event.preventDefault();
        if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
            this.selectedFile = event.dataTransfer.files[0];
        }
    }

    canUpload(): boolean {
        return !!(this.uploadName && this.uploadFormat && this.selectedFile);
    }

    uploadDataset() {
        if (!this.canUpload()) return;

        this.submitting = true;
        this.api.uploadDataset(this.selectedFile!, this.uploadName, this.uploadFormat).subscribe({
            next: (result) => {
                console.log('Upload successful:', result);
                this.showUploadModal = false;
                this.refreshDatasets();
                this.resetUploadForm();
                this.submitting = false;
            },
            error: (err) => {
                console.error('Upload failed:', err);
                alert('Upload failed: ' + (err.error?.detail || err.message));
                this.submitting = false;
            }
        });
    }

    resetUploadForm() {
        this.uploadName = '';
        this.uploadFormat = 'segy';
        this.selectedFile = null;
    }
}
