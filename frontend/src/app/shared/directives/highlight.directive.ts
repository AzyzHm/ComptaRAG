import { Directive, ElementRef, HostListener, Input, inject } from '@angular/core';

@Directive({
  selector: '[appHighlight]',
  standalone: true
})
export class HighlightDirective {
  private readonly el = inject(ElementRef<HTMLElement>);

  @Input('appHighlight') highlightColor = '#fef08a';

  @HostListener('mouseenter')
  onMouseEnter(): void {
    this.setBackgroundColor(this.highlightColor);
  }

  @HostListener('mouseleave')
  onMouseLeave(): void {
    this.setBackgroundColor('');
  }

  private setBackgroundColor(color: string): void {
    this.el.nativeElement.style.backgroundColor = color;
  }
}
