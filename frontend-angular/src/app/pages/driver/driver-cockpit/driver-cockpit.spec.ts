import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DriverCockpit } from './driver-cockpit';

describe('DriverCockpit', () => {
  let component: DriverCockpit;
  let fixture: ComponentFixture<DriverCockpit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DriverCockpit]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DriverCockpit);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
