import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { Icons } from './shared/icons';

interface NavItem {
    path: string;
    label: string;
    icon: string;
}

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent {
    title = 'Promethium';
    appVersion = '1.0.0';

    mainNavItems: NavItem[] = [
        { path: '/dashboard', label: 'Dashboard', icon: Icons.dashboard },
        { path: '/datasets', label: 'Datasets', icon: Icons.database },
        { path: '/pipelines', label: 'Pipelines', icon: Icons.workflow },
        { path: '/jobs', label: 'Jobs', icon: Icons.zap },
        { path: '/models', label: 'Models', icon: Icons.brain },
        { path: '/experiments', label: 'Experiments', icon: Icons.flask },
        { path: '/benchmarks', label: 'Benchmarks', icon: Icons.barChart },
        { path: '/results', label: 'Results', icon: Icons.activity },
    ];

    secondaryNavItems: NavItem[] = [
        { path: '/system', label: 'System', icon: Icons.server },
        { path: '/docs', label: 'Documentation', icon: Icons.book },
        { path: '/settings', label: 'Settings', icon: Icons.settings },
    ];
}
