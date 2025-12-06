import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VehicleDetails } from './vehicle-details';

describe('VehicleDetails', () => {
  let component: VehicleDetails;
  let fixture: ComponentFixture<VehicleDetails>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VehicleDetails]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VehicleDetails);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
