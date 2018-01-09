#ifndef _ATTRIBUTES_ATTRIBUTES_H_
#define _ATTRIBUTES_ATTRIBUTES_H_

#include <iostream>
#include <vector>
#include <array>
#include <stdexcept>
#include <functional>
#include <gsl/multi_span>

/*
 REFERENCES
 [1] gsl from https://github.com/Microsoft/GSL (#548)
 */
namespace attributes {

template <class MetaInfo, class A, class Owner>
class ReadOnlyAttribute {
    friend Owner;
protected:
    A value_data;
    ReadOnlyAttribute(const ReadOnlyAttribute&) = default;
    ReadOnlyAttribute& operator=(const ReadOnlyAttribute&) = default;
public:
    using value_type = A;
    ReadOnlyAttribute(const A& a): value_data{a} {}
    ReadOnlyAttribute(): value_data{} {}
    
    operator const value_type&() const { return value_data; }
    const value_type& value() const { return value_data; }
    const value_type* operator->() const { return &value_data; }
protected:
    ReadOnlyAttribute& operator=(const value_type& v) { value_data=v; return *this; }    
    value_type* operator->() { return &value_data; }
    value_type& value() { return value_data; }
};

template <class MetaInfo, class A, class Owner>
class Attribute : public ReadOnlyAttribute<MetaInfo, A, Owner> {
    friend Owner;
 public:
    using value_type = A;
    using ReadOnlyAttribute<MetaInfo, A, Owner>::ReadOnlyAttribute;
    using ReadOnlyAttribute<MetaInfo, A, Owner>::operator=;
    using ReadOnlyAttribute<MetaInfo, A, Owner>::operator->;
    using ReadOnlyAttribute<MetaInfo, A, Owner>::value;
};

template<size_t N>
using DynamicArraySizeFunctions = std::array<std::function<size_t(void)>,N>;

template<class A, class D>
auto constexpr attribute_as_multi_span(A array, const std::array<D,1> &dims) { return gsl::as_multi_span(array, gsl::dim(dims[0])); }
template<class A, class D>
auto constexpr attribute_as_multi_span(A array, const std::array<D,2> &dims) { return gsl::as_multi_span(array, gsl::dim(dims[0]), gsl::dim(dims[1])); }
template<class A, class D>
auto constexpr attribute_as_multi_span(A array, const std::array<D,3> &dims) { return gsl::as_multi_span(array, gsl::dim(dims[0]), gsl::dim(dims[1]), gsl::dim(dims[2])); }
template<class A, class D>
auto constexpr attribute_as_multi_span(A array, const std::array<D,4> &dims) { return gsl::as_multi_span(array, gsl::dim(dims[0]), gsl::dim(dims[1]), gsl::dim(dims[2]), gsl::dim(dims[3])); }

template <class MetaInfo, class A, class Owner, size_t N>
class DynamicArrayAttribute : public ReadOnlyAttribute<MetaInfo, std::vector<A>, Owner> {
    friend Owner;
 public:
    using dynamic_array_size_functions_type = DynamicArraySizeFunctions<N>;
    using value_type = typename ReadOnlyAttribute<MetaInfo, std::vector<A>, Owner>::value_type;
    using inner_value_type = typename value_type::value_type;
    DynamicArrayAttribute(dynamic_array_size_functions_type _sizeFun) : ReadOnlyAttribute<MetaInfo, std::vector<A>, Owner>{}, sizeFun(_sizeFun) { adjust_size(); }
    
    DynamicArrayAttribute& operator=(const value_type& v) {
        adjust_size();
        if (this->value_data.size() != v.size()) {
            throw std::out_of_range("ArrayAttribute::=, sizes do not match.");
        }
        this->value_data=v; 
        return *this; 
    }
    
    inner_value_type& operator[](size_t idx) { return this->value_data[idx]; }
    const inner_value_type& operator[](size_t idx) const { return this->value_data[idx]; }
    inner_value_type& at(size_t idx) { return this->value_data.at(idx); }
    const inner_value_type& at(size_t idx) const { return this->value_data.at(idx); }
    auto span() { return array_as_span; }
    auto span() const { return array_as_span; }
    const auto& dimensions() const { return this->sizes; }
    auto size() const { return this->value_data.size(); }
    inner_value_type& operator[](gsl::index<N> idx) { return span()[idx]; }
    const inner_value_type& operator[](gsl::index<N> idx) const { return span()[idx]; }
    auto begin() { return this->value_data.begin(); }
    auto end() { return this->value_data.end(); }
    
private:
    static auto __helper() {
        std::array<size_t,N> sizes;
        inner_value_type dummy;
        return attribute_as_multi_span(&dummy,sizes);        
    }
protected:
    dynamic_array_size_functions_type sizeFun;
    std::array<size_t,N> sizes;
    decltype(__helper()) array_as_span;
    void adjust_size() {
        size_t n = 1;
        for(size_t i=0;i<N;i++) {
            sizes[i] = sizeFun[i]();
            n *= sizes[i];
        }
        this->value_data.resize(n);
        array_as_span = attribute_as_multi_span(this->value_data.data(),sizes);
    }
};

template<size_t Dim0, size_t... Dims>
struct Prod {
    static constexpr size_t value = Dim0 * Prod<Dims...>::value;
};
template<size_t Dim0>
struct Prod<Dim0> {
    static constexpr size_t value = Dim0;
};

template <class MetaInfo, class A, class Owner, size_t N, size_t MAX_FLAT_SIZE>
class AutomaticArrayAttribute : public ReadOnlyAttribute<MetaInfo, std::array<A, MAX_FLAT_SIZE>, Owner> {
    friend Owner;
 public:
    using dynamic_array_size_functions_type = DynamicArraySizeFunctions<N>;
    using value_type = typename ReadOnlyAttribute<MetaInfo, std::array<A,MAX_FLAT_SIZE>, Owner>::value_type;
    using inner_value_type = typename value_type::value_type;
    AutomaticArrayAttribute(dynamic_array_size_functions_type _sizeFun) : ReadOnlyAttribute<MetaInfo, std::array<A,MAX_FLAT_SIZE>, Owner>{}, sizeFun(_sizeFun) { adjust_size(); }
    
    AutomaticArrayAttribute& operator=(const value_type& v) {
        adjust_size();
        if (this->value_data.size() != v.size()) {
            throw std::out_of_range("ArrayAttribute::=, sizes do not match.");
        }
        this->value_data=v; 
        return *this; 
    }
    
    inner_value_type& operator[](size_t idx) { return this->value_data[idx]; }
    const inner_value_type& operator[](size_t idx) const { return this->value_data[idx]; }
    inner_value_type& at(size_t idx) { return this->value_data.at(idx); }
    const inner_value_type& at(size_t idx) const { return this->value_data.at(idx); }
    auto span() { return array_as_span; }
    auto span() const { return array_as_span; }
    const auto& dimensions() const { return this->sizes; }
    auto size() const { return this->value_data.size(); }
    inner_value_type& operator[](gsl::index<N> idx) { return span()[idx]; }
    const inner_value_type& operator[](gsl::index<N> idx) const { return span()[idx]; }
    auto begin() { return this->value_data.begin(); }
    auto end() { return this->value_data.end(); }
    auto begin() const { return this->value_data.begin(); }
    auto end() const { return this->value_data.end(); }

private:
    static auto __helper() {
        std::array<size_t,N> sizes;
        inner_value_type dummy;
        return attribute_as_multi_span(&dummy,sizes);        
    }
protected:
    dynamic_array_size_functions_type sizeFun;
    std::array<size_t,N> sizes;
    decltype(__helper()) array_as_span;
    void adjust_size() {
        size_t n = 1;
        for(size_t i=0;i<N;i++) {
            sizes[i] = sizeFun[i]();
            n *= sizes[i];
        }
        if (n>MAX_FLAT_SIZE) {
            throw std::out_of_range("ArrayAttribute::=, sizes too large.");            
        }
        array_as_span = attribute_as_multi_span(this->value_data.data(),sizes);
    }
};

}

#endif // _ATTRIBUTES_ATTRIBUTES_H_

