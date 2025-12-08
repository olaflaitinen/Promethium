import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, Model, ModelStatus, ModelType } from '../../services/api.service';
import { Icons } from '../../shared/icons';

@Component({
    selector: 'app-models',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './models.component.html',
    styleUrls: ['./models.component.css']
})
export class ModelsComponent implements OnInit {
    icons = Icons;
    models: Model[] = [];
    loading = true;
    error: string | null = null;

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.loadModels();
    }

    loadModels() {
        this.loading = true;
        this.error = null;

        this.api.getModels().subscribe({
            next: (models) => {
                this.models = models;
                this.loading = false;
            },
            error: (err) => {
                this.error = 'Failed to load models';
                this.loading = false;
            }
        });
    }

    getStatusBadgeClass(status: ModelStatus): string {
        switch (status) {
            case ModelStatus.READY: return 'pm-badge-success';
            case ModelStatus.TRAINING: return 'pm-badge-info';
            case ModelStatus.PENDING: return 'pm-badge-warning';
            case ModelStatus.FAILED: return 'pm-badge-error';
            default: return 'pm-badge-neutral';
        }
    }

    getModelTypeLabel(type: ModelType): string {
        switch (type) {
            case ModelType.UNET: return 'U-Net';
            case ModelType.AUTOENCODER: return 'Autoencoder';
            case ModelType.GAN: return 'GAN';
            case ModelType.TRANSFORMER: return 'Transformer';
            default: return type;
        }
    }

    formatMetric(value: number | undefined, decimals: number = 2): string {
        if (value === undefined) return '-';
        return value.toFixed(decimals);
    }
}
