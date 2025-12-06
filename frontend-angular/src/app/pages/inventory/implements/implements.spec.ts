import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Implements } from './implements';

describe('Implements', () => {
  let component: Implements;
  let fixture: ComponentFixture<Implements>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Implements]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Implements);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
