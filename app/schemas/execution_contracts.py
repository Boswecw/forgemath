from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ZERO = Decimal("0")
ONE = Decimal("1")


class ExecutionContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LaneSpecPayloadContract(ExecutionContractModel):
    contract_version: str = Field(min_length=1, max_length=64)
    lane_id: str = Field(min_length=1, max_length=255)


class VariableRegistryPayloadContract(ExecutionContractModel):
    variables: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_variables(self) -> "VariableRegistryPayloadContract":
        cleaned = [item.strip() for item in self.variables if item and item.strip()]
        if len(cleaned) != len(self.variables):
            raise ValueError("variables must be non-blank.")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("variables must be unique.")
        self.variables = cleaned
        return self


class ThresholdBandContract(ExecutionContractModel):
    label: str = Field(min_length=1, max_length=255)
    min_inclusive: Decimal
    max_exclusive: Decimal | None = None
    max_inclusive: Decimal | None = None

    @model_validator(mode="after")
    def validate_band(self) -> "ThresholdBandContract":
        if (self.max_exclusive is None) == (self.max_inclusive is None):
            raise ValueError("threshold bands require exactly one of max_exclusive or max_inclusive.")
        maximum = self.max_exclusive if self.max_exclusive is not None else self.max_inclusive
        if maximum is None:
            raise ValueError("threshold bands require an upper bound.")
        if self.min_inclusive < 0 or maximum > 1 or self.min_inclusive > maximum:
            raise ValueError("threshold bands must stay within [0,1].")
        return self


class ThresholdSetPayloadContract(ExecutionContractModel):
    bands: list[ThresholdBandContract] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_band_topology(self) -> "ThresholdSetPayloadContract":
        labels: set[str] = set()
        prior_upper: Decimal | None = None
        prior_inclusive = False

        for index, band in enumerate(self.bands):
            if band.label in labels:
                raise ValueError("threshold band labels must be unique.")
            labels.add(band.label)
            upper = band.max_inclusive if band.max_inclusive is not None else band.max_exclusive
            if upper is None:
                raise ValueError("threshold bands require an upper bound.")
            current_inclusive = band.max_inclusive is not None

            if index == 0:
                if band.min_inclusive != ZERO:
                    raise ValueError("threshold bands must start at min_inclusive=0.")
            elif prior_upper is not None:
                if band.min_inclusive < prior_upper:
                    raise ValueError("threshold bands may not overlap.")
                if band.min_inclusive > prior_upper:
                    raise ValueError("threshold bands may not leave gaps.")
                if prior_inclusive:
                    raise ValueError(
                        "threshold bands may not use an inclusive upper bound before the terminal band."
                    )

            prior_upper = upper
            prior_inclusive = current_inclusive

        if prior_upper != ONE or not prior_inclusive:
            raise ValueError("threshold bands must terminate with max_inclusive=1.")
        return self


class VerificationBurdenWeightsContract(ExecutionContractModel):
    w_I: Decimal
    w_V: Decimal
    w_R: Decimal
    w_X: Decimal
    w_D: Decimal
    w_U: Decimal

    @model_validator(mode="after")
    def validate_weights(self) -> "VerificationBurdenWeightsContract":
        values = self.model_dump(mode="python")
        if any(value < ZERO for value in values.values()):
            raise ValueError("verification burden weights must be non-negative.")
        if sum(values.values(), ZERO) != ONE:
            raise ValueError("verification burden weights must sum to 1.")
        return self


class VerificationBurdenCapsContract(ExecutionContractModel):
    I_cap: Decimal
    V_cap: Decimal
    R_cap: Decimal
    X_cap: Decimal
    D_cap: Decimal

    @model_validator(mode="after")
    def validate_caps(self) -> "VerificationBurdenCapsContract":
        values = self.model_dump(mode="python")
        if any(value <= ZERO for value in values.values()):
            raise ValueError("verification burden caps must be greater than zero.")
        return self


class VerificationBurdenParameterContract(ExecutionContractModel):
    weights: VerificationBurdenWeightsContract
    caps: VerificationBurdenCapsContract


class RecurrencePressureWeightsContract(ExecutionContractModel):
    w30: Decimal
    w90: Decimal
    wsame: Decimal
    wcross: Decimal
    wpost: Decimal

    @model_validator(mode="after")
    def validate_weights(self) -> "RecurrencePressureWeightsContract":
        values = self.model_dump(mode="python")
        if any(value < ZERO for value in values.values()):
            raise ValueError("recurrence pressure weights must be non-negative.")
        if sum(values.values(), ZERO) != ONE:
            raise ValueError("recurrence pressure weights must sum to 1.")
        return self


class RecurrencePressureSaturationContract(ExecutionContractModel):
    k30: Decimal
    k90: Decimal
    ksame: Decimal
    kcross: Decimal
    kpost: Decimal

    @model_validator(mode="after")
    def validate_saturation(self) -> "RecurrencePressureSaturationContract":
        values = self.model_dump(mode="python")
        if any(value <= ZERO for value in values.values()):
            raise ValueError("recurrence pressure saturation coefficients must be greater than zero.")
        return self


class RecurrencePressureParameterContract(ExecutionContractModel):
    weights: RecurrencePressureWeightsContract
    saturation: RecurrencePressureSaturationContract


class ExposureFactorCoefficientContract(ExecutionContractModel):
    alpha_pub: Decimal
    alpha_op: Decimal
    alpha_persist: Decimal
    alpha_approve: Decimal
    alpha_cross: Decimal
    alpha_boundary: Decimal

    @model_validator(mode="after")
    def validate_coefficients(self) -> "ExposureFactorCoefficientContract":
        values = self.model_dump(mode="python")
        if any(value < ZERO or value > ONE for value in values.values()):
            raise ValueError("exposure factor coefficients must stay within [0,1].")
        return self


class ExposureFactorParameterContract(ExecutionContractModel):
    coefficients: ExposureFactorCoefficientContract
