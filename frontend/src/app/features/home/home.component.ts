import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';

import { ButtonComponent } from '@shared/components/button/button.component';

interface HomeHighlight {
  title: string;
  body: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [ButtonComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HomeComponent {
  private readonly router = inject(Router);

  protected readonly highlights: HomeHighlight[] = [
    {
      title: 'IFRS, grounded',
      body: 'Every answer is traced back to the standard it comes from, not guessed from memory.'
    },
    {
      title: 'Tunisian fiscal law',
      body: 'Trained on the Tunisian tax code so local questions get local answers.'
    },
    {
      title: 'French or English',
      body: 'Ask however you think. ComptaRAG follows you between the two.'
    }
  ];

  protected goToRegister(): void {
    this.router.navigate(['/login'], { queryParams: { mode: 'register' } });
  }

  protected goToSignIn(): void {
    this.router.navigateByUrl('/login');
  }
}
