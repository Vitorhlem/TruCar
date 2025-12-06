import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Fines } from './fines';

describe('Fines', () => {
  let component: Fines;
  let fixture: ComponentFixture<Fines>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Fines]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Fines);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
