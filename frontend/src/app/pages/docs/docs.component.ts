import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icons } from '../../shared/icons';

interface DocSection {
    title: string;
    icon: keyof typeof Icons;
    items: { name: string; description: string; href: string; }[];
}

@Component({
    selector: 'app-docs',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './docs.component.html',
    styleUrls: ['./docs.component.css']
})
export class DocsComponent {
    icons = Icons;

    docSections: DocSection[] = [
        {
            title: 'Getting Started',
            icon: 'play',
            items: [
                { name: 'Quick Start Guide', description: 'Set up Promethium in minutes', href: '#' },
                { name: 'Installation', description: 'System requirements and installation steps', href: '#' },
                { name: 'Configuration', description: 'Environment variables and settings', href: '#' }
            ]
        },
        {
            title: 'User Guide',
            icon: 'book',
            items: [
                { name: 'Working with Datasets', description: 'Upload, manage, and preprocess seismic data', href: '#' },
                { name: 'Running Pipelines', description: 'Configure and execute reconstruction jobs', href: '#' },
                { name: 'Model Training', description: 'Train custom AI/ML models', href: '#' },
                { name: 'Results Analysis', description: 'Visualize and export results', href: '#' }
            ]
        },
        {
            title: 'API Reference',
            icon: 'server',
            items: [
                { name: 'REST API', description: 'Complete API endpoints documentation', href: 'http://localhost:8000/docs' },
                { name: 'Data Schemas', description: 'Request and response formats', href: '#' },
                { name: 'Authentication', description: 'API keys and security', href: '#' }
            ]
        },
        {
            title: 'Architecture',
            icon: 'layers',
            items: [
                { name: 'System Overview', description: 'High-level architecture diagram', href: '#' },
                { name: 'ML Pipeline', description: 'AI/ML processing workflow', href: '#' },
                { name: 'Data Engineering', description: 'Storage and processing infrastructure', href: '#' }
            ]
        }
    ];

    getIcon(name: string): string {
        return Icons[name as keyof typeof Icons] || '';
    }
}

