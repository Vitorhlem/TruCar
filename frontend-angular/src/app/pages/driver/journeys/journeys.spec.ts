import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Journeys } from './journeys';

describe('Journeys', () => {
  let component: Journeys;
  let fixture: ComponentFixture<Journeys>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Journeys]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Journeys);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
