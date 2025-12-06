import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Costs } from './costs';

describe('Costs', () => {
  let component: Costs;
  let fixture: ComponentFixture<Costs>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Costs]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Costs);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
