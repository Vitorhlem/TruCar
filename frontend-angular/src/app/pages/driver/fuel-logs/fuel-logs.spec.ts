import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FuelLogs } from './fuel-logs';

describe('FuelLogs', () => {
  let component: FuelLogs;
  let fixture: ComponentFixture<FuelLogs>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FuelLogs]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FuelLogs);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
