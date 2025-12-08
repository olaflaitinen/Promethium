import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Icons } from '../../shared/icons';

@Component({
    selector: 'app-settings',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './settings.component.html',
    styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {
    icons = Icons;

    settings = {
        darkMode: true,
        notifications: true,
        autoRefresh: true,
        apiUrl: 'http://localhost:8000',
        apiTimeout: 30,
        defaultModel: 'unet-v2',
        computeDevice: 'auto',
        precision: 'float32'
    };

    saveSettings() {
        localStorage.setItem('promethium_settings', JSON.stringify(this.settings));
        // simple toast or alert - in a real app use a notification service
        alert('Settings saved successfully!');
    }

    resetSettings() {
        if (confirm('Are you sure you want to reset all settings to default?')) {
            this.settings = {
                darkMode: true,
                notifications: true,
                autoRefresh: true,
                apiUrl: 'http://localhost:8000',
                apiTimeout: 30,
                defaultModel: 'unet-v2',
                computeDevice: 'auto',
                precision: 'float32'
            };
        }
    }

    ngOnInit() {
        const saved = localStorage.getItem('promethium_settings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
    }
}
